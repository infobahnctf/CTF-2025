import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly

CLK_PERIOD_NS = 10

# -----------------------------
# Register map (byte addresses)
# -----------------------------
REG_KEY     = 0x00
REG_CTRL    = 0x04
REG_STATUS  = 0x08
REG_CTEXT   = 0x0C
REG_INDEX   = 0x10
REG_LENGTH  = 0x14

# CTRL bits on write
CTRL_START    = 1 << 0
CTRL_CLR_DONE = 1 << 1
CTRL_AUTO_INC = 1 << 2

# -----------------------------
# Expected ROM (big-endian) for the flag
# ASCII: infobahn{b1t5tr4mR3vers1ngCanB3 H4rd, bUt somet1mes you don't n33d to reverse everything :0}
# -----------------------------
FLAG_ROM = [
    0x696e666f, 0x6261686e, 0x7b623174, 0x35747234, 0x6d523376,
    0x65727331, 0x6e674361, 0x6e423320, 0x48347264, 0x2c206255,
    0x7420736f, 0x6d657431, 0x6d657320, 0x796f7520, 0x646f6e27,
    0x74206e33, 0x33642074, 0x6f207265, 0x76657273, 0x65206576,
    0x65727974, 0x68696e67, 0x203a307d,
]
FLAG_LEN = len(FLAG_ROM)

def rotl8(x: int) -> int:
    x &= 0xFFFFFFFF
    return ((x << 8) & 0xFFFFFFFF) | ((x >> 24) & 0xFF)

def word(u32: int) -> int:
    return u32 & 0xFFFFFFFF


# -----------------------------
# Minimal AXI4-Lite Master (32-bit)
# -----------------------------
class AxiLiteMasterMini:
    def __init__(self, dut):
        self.dut = dut
        dut.S_AWVALID.value = 0
        dut.S_WVALID.value  = 0
        dut.S_BREADY.value  = 0
        dut.S_ARVALID.value = 0
        dut.S_RREADY.value  = 0
        dut.S_AWADDR.value = 0
        dut.S_WDATA.value  = 0
        dut.S_WSTRB.value  = 0
        dut.S_ARADDR.value = 0

    async def write(self, addr: int, data: int, wstrb: int = 0xF):
        dut = self.dut
        dut.S_AWADDR.value  = addr
        dut.S_AWVALID.value = 1
        dut.S_WDATA.value   = data & 0xFFFFFFFF
        dut.S_WSTRB.value   = wstrb & 0xF
        dut.S_WVALID.value  = 1

        aw_done = False
        w_done  = False
        while not (aw_done and w_done):
            await RisingEdge(dut.ACLK)
            if not aw_done and dut.S_AWREADY.value.integer:
                dut.S_AWVALID.value = 0
                aw_done = True
            if not w_done and dut.S_WREADY.value.integer:
                dut.S_WVALID.value = 0
                w_done = True

        dut.S_BREADY.value = 1
        while True:
            await RisingEdge(dut.ACLK)
            if dut.S_BVALID.value.integer:
                await ReadOnly()
                await RisingEdge(dut.ACLK)
                dut.S_BREADY.value = 0
                break

    async def read(self, addr: int) -> int:
        dut = self.dut
        dut.S_ARADDR.value  = addr
        dut.S_ARVALID.value = 1

        while True:
            await RisingEdge(dut.ACLK)
            if dut.S_ARREADY.value.integer:
                dut.S_ARVALID.value = 0
                break

        dut.S_RREADY.value = 1
        while True:
            await RisingEdge(dut.ACLK)
            if dut.S_RVALID.value.integer:
                await ReadOnly()
                data = dut.S_RDATA.value.integer & 0xFFFFFFFF
                await RisingEdge(dut.ACLK)
                dut.S_RREADY.value = 0
                return data


class Axil:
    def __init__(self, dut):
        self.m = AxiLiteMasterMini(dut)

    async def write32(self, addr: int, data: int, wstrb: int = 0xF):
        await self.m.write(addr, data, wstrb=wstrb)

    async def read32(self, addr: int) -> int:
        return await self.m.read(addr)


async def reset(dut, cycles=5):
    dut.ARESETn.value = 0
    for _ in range(cycles):
        await RisingEdge(dut.ACLK)
    dut.ARESETn.value = 1
    await RisingEdge(dut.ACLK)


# -----------------------------
# Tests
# -----------------------------
@cocotb.test()
async def test_axi_reset(dut):
    # Verify initial register values after reset.
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD_NS, units="ns").start())
    await reset(dut)
    axil = Axil(dut)

    length = await axil.read32(REG_LENGTH)
    assert length == FLAG_LEN, f"REG_LENGTH expected {FLAG_LEN}, got 0x{length:08x}"

    key   = await axil.read32(REG_KEY)
    idx   = await axil.read32(REG_INDEX)
    stat  = await axil.read32(REG_STATUS)
    ctext = await axil.read32(REG_CTEXT)
    ctrlr = await axil.read32(REG_CTRL)

    assert key == 0
    assert idx == 0
    assert stat & 1 == 0
    assert ctext == 0
    assert ctrlr in (0, CTRL_AUTO_INC), f"CTRL readback unexpected: 0x{ctrlr:08x}"


@cocotb.test()
async def test_wstrb_on_key(dut):
    # Test partial write using wstrb on the KEY register.
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD_NS, units="ns").start())
    await reset(dut)
    axil = Axil(dut)

    await axil.write32(REG_KEY, 0xAABBCCDD, wstrb=0b0101)
    rd = await axil.read32(REG_KEY)
    assert rd == 0x00BB00DD, f"WSTRB write mismatch: got 0x{rd:08x}"


@cocotb.test()
async def test_single_encrypt_and_done(dut):
    # Test single encryption cycle, DONE flag assertion, stickiness, and clearing.
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD_NS, units="ns").start())
    await reset(dut)
    axil = Axil(dut)

    key = 0x11223344
    idx = 3
    await axil.write32(REG_KEY,   key)
    await axil.write32(REG_INDEX, idx)

    await axil.write32(REG_CTRL, CTRL_START)

    stat = 0
    for _ in range(5):
        stat = await axil.read32(REG_STATUS)
        if stat & 1:
            break
        await RisingEdge(dut.ACLK)
    assert stat & 1, "DONE did not assert"

    ctext = await axil.read32(REG_CTEXT)
    expected = rotl8(word(FLAG_ROM[idx] ^ key))
    assert ctext == expected, f"Ciphertext mismatch. got=0x{ctext:08x}, expected=0x{expected:08x}"

    stat2 = await axil.read32(REG_STATUS)
    assert stat2 & 1, "DONE should be sticky"

    await axil.write32(REG_CTRL, CTRL_CLR_DONE)
    stat3 = await axil.read32(REG_STATUS)
    assert (stat3 & 1) == 0, "DONE didn't clear after CLR_DONE"


@cocotb.test()
async def test_auto_inc_stream_and_wrap(dut):
    # Test auto-increment mode for streaming all blocks and index wrap-around.
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD_NS, units="ns").start())
    await reset(dut)
    axil = Axil(dut)

    key = 0xCAFEBABE
    await axil.write32(REG_KEY,   key)
    await axil.write32(REG_INDEX, 0)

    await axil.write32(REG_CTRL, CTRL_AUTO_INC)

    got = []
    for _ in range(FLAG_LEN):
        await axil.write32(REG_CTRL, CTRL_AUTO_INC | CTRL_START)

        for _ in range(8):
            stat = await axil.read32(REG_STATUS)
            if stat & 1:
                break
            await RisingEdge(dut.ACLK)

        ctext = await axil.read32(REG_CTEXT)
        got.append(ctext)
        await axil.write32(REG_CTRL, CTRL_CLR_DONE)

    exp = [rotl8(word(p ^ key)) for p in FLAG_ROM]
    assert got == exp, (
        f"AUTO_INC stream mismatch.\n"
        f"exp={list(map(lambda x:f'0x{x:08x}', exp))}\n"
        f"got={list(map(lambda x:f'0x{x:08x}', got))}"
    )

    idx = await axil.read32(REG_INDEX)
    assert idx == 0, f"INDEX should wrap to 0 after {FLAG_LEN} blocks, got {idx}"


@cocotb.test()
async def test_out_of_range_index(dut):
    # Test encryption with out-of-range index.
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD_NS, units="ns").start())
    await reset(dut)
    axil = Axil(dut)

    key = 0x01020304
    await axil.write32(REG_KEY, key)
    await axil.write32(REG_INDEX, 99)

    await axil.write32(REG_CTRL, CTRL_START)
    for _ in range(5):
        if (await axil.read32(REG_STATUS)) & 1:
            break
        await RisingEdge(dut.ACLK)

    ctext = await axil.read32(REG_CTEXT)
    expected = rotl8(word(0 ^ key))
    assert ctext == expected, f"OOR index ciphertext mismatch. got=0x{ctext:08x}, expected=0x{expected:08x}"


@cocotb.test()
async def test_aw_w_skew_fuzzer(dut):
    # Fuzz test for AW/W channel skew with random writes, then verify encryption.
    cocotb.start_soon(Clock(dut.ACLK, CLK_PERIOD_NS, units="ns").start())
    await reset(dut)
    axil = Axil(dut)

    rnd = random.Random(1234)
    for _ in range(50):
        addr  = rnd.choice([REG_KEY, REG_INDEX, REG_CTRL])
        data  = rnd.getrandbits(32)
        wstrb = rnd.choice([0x1, 0x3, 0xF])
        await axil.write32(addr, data, wstrb=wstrb)

    await axil.write32(REG_KEY, 0x0)
    await axil.write32(REG_INDEX, 0)
    await axil.write32(REG_CTRL, CTRL_START)
    for _ in range(5):
        if (await axil.read32(REG_STATUS)) & 1:
            break
        await RisingEdge(dut.ACLK)
    ctext = await axil.read32(REG_CTEXT)
    expected = rotl8(word(FLAG_ROM[0] ^ 0))
    assert ctext == expected, f"Post-fuzz encrypt check failed. got=0x{ctext:08x}, expected=0x{expected:08x}"
