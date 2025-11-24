# LUTsOfFun

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [NeKroFR](https://github.com/NeKroFR)                                                       |
| **Category** | Rev                                                                                         |
| **Solves**   | 2                                                                                           |
| **Files**    | [crackme.bit](crackme.bit) [cstr.xdc](cstr.xdc)                                             |

# Description

A friend gave me this Bitstream. He told me he hid a secret message and that it would be a LUT of fun to recover it!

# Solve

This challenge provide us a Xilinx bitstream for the `7a100tcsg324` target.

```sh
❯ file crackme.bit
crackme.bit: Xilinx BIT data - from axi_encrypt_slave;UserID=0XFFFFFFFF;Version=2025.1;SW_CRC=62685c4c - for 7a100tcsg324 - built 2025/10/17(11:29:10) - data length 0x3a607c
```

Looking online we can see that it part of the gen7 and we can recover the [FASM](https://byu-cpe.github.io/ComputingBootCamp/tutorials/fasm/) representation with [prjxray](https://github.com/f4pga/prjxray) then we can convert it to verilog and the xdc file with [fasm2bel](https://github.com/chipsalliance/f4pga-xc-fasm2bels).

Now you can reverse it using tools like [Vivado](https://www.xilinx.com/support/download.html) or [hal](https://github.com/emsec/hal). You can also write testbenches to analyze the behaviour of the bitstream dynamically using for example [cocotb](https://www.cocotb.org/).

## What's Inside the bitstream ?

The bitstream is an AXI slave, which let us set the values of two registers: `REG_KEY` and `REG_INDEX`. We can also get a sample of the flag encrypted with this basic function:

```v
// ROTL8(plaintext ^ key)
function automatic [BLOCK_SIZE-1:0] round (
    input logic [BLOCK_SIZE-1:0] s,
    input logic [KEY_SIZE-1:0] k
);
    logic [BLOCK_SIZE-1:0] tmp;
    tmp = s ^ k;
    return {tmp[BLOCK_SIZE-9:0], tmp[BLOCK_SIZE-1:BLOCK_SIZE-8]};
endfunction
```

The flag is stored inside a ROM:

```v
localparam logic [31:0] FLAG_ROM [0:FLAG_LEN-1] = '{
    32'h696e666f, 32'h6261686e, 32'h7b623174, 32'h35747234, 32'h6d523376,
    32'h65727331, 32'h6e674361, 32'h6e423320, 32'h48347264, 32'h2c206255,
    32'h7420736f, 32'h6d657431, 32'h6d657320, 32'h796f7520, 32'h646f6e27,
    32'h74206e33, 32'h33642074, 32'h6f207265, 32'h76657273, 32'h65206576,
    32'h65727974, 32'h68696e67, 32'h203a307d
};
```

And we can choose our word using the `REG_INDEX`.

## Why it's hard to reverse?

Due to the synthesis, the circuit as been optimized and the ROM as been hardcoded inside LUTS. And because of the fact the value will depend of the value of the index we try to access, we can't directly identify the bytes of the FLAG.

## How to solve then?

Once you identifyed how to reset and how to get some ciphertext, you will get:

```py
ROTL8(plaintext[0] ^ 0) = ROTL8(0x696e666f ^ 0)
                        = ROTL8(0x696e666f)
                        = 0x6e666f69
```

knowing that the flag format is: `infobahn{...}` You will see that `0x6e666f69` is 4 bytes, and from that trying to recover **"info"** (`0x696e666f`) And you can see that just doing a simple bitshift of 8 you recover this part of the flag. Then you just have to increment `REG_INDEX` until you recovered the whole flag.
