import os
import re 
BYTECODE_NAMES = {
    0xbb: "SwitchOnGeneratorState",
    0x1b: "Mov",
    0x70: "InvokeIntrinsic",
    0xd1: "Star0",
    0xd0: "Star1",
    0xcf: "Star2",
    0xce: "Star3",
    0xcd: "Star4",
    0xcc: "Star5",
    0xcb: "Star6",
    0xca: "Star7",
    0xc9: "Star8",
    0xc8: "Star9",
    0xc7: "Star10",
    0xc6: "Star11",
    0xc5: "Star12",
    0xc4: "Star13",
    0xc3: "Star14",
    0xc2: "Star15",
    0xbc: "SuspendGenerator",
    0xbd: "ResumeGenerator",
    0x1a: "Star",
    0xad: "SwitchOnSmiNoFeedback",
    0x0b: "Ldar",
    0xb4: "Throw",
    0xb6: "Return",
    0x23: "LdaGlobal",
    0x13: "LdaConstant",
    0x69: "CallUndefinedReceiver0",
    0x6a: "CallUndefinedReceiver1",
    0x6b: "CallUndefinedReceiver2",
    0x33: "GetNamedProperty",
    0x0c: "LdarZero",
    0x65: "CallProperty0",
    0x66: "CallProperty1",
    0x67: "CallProperty2",
    0x83: "CreateArrayLiteral",
    0x53: "BitwiseXorSmi",
    0x3d: "StaInArrayLiteral",
    0x0d: "LdaSmi",
    0xbe: "GetIterator",
    0x12: "LdaFalse",
    0x11: "LdaTrue",
    0x10: "LdaTheHole",
    0x0e: "LdaUndefined",
    0x94: "JumpLoop",
    0x95: "Jump",
    0xa2: "JumpIfToBooleanTrue",
    0xa3: "JumpIfToBooleanFalse",
    0xa4: "JumpIfTrue",
    0xa5: "JumpIfFalse",
    0xaa: "JumpIfUndefinedOrNull",
    0xab: "JumpIfJSReceiver",
    0x6d: "CallRuntime",
    0xb3: "SetPendingMessage",
    0x1e: "TestReferenceEqual",
    0xb5: "ReThrow",
    0x3f: "Add",
    0x41: "Mul",
    0x74: "TestEqual",
    0x76: "TestLessThan",
    0x4c: "AddSmi",
    0x4e: "MulSmi",
    0x35: "GetKeyedProperty",
}

OPERAND_SPEC = {
    "SwitchOnGeneratorState": [("reg",1), ("imm",1), ("imm",1)],
    "Mov": [("reg",1), ("reg",1)],
    "InvokeIntrinsic": [("intr",1), ("regdif",2)],
    "Star0": [],
    "Star1": [],
    "Star2": [],
    "Star3": [],
    "Star4": [],
    "Star5": [],
    "Star6": [],
    "Star7": [],
    "Star8": [],
    "Star9": [],
    "Star10": [],
    "Star11": [],
    "Star12": [],
    "Star13": [],
    "Star14": [],
    "Star15": [],
    "SuspendGenerator": [("reg",1), ("regdif",2), ("uimm",1)],
    "ResumeGenerator": [("reg",1), ("regdif",2)],
    "Star": [("reg",1)],
    "SwitchOnSmiNoFeedback": [("uimm",1),("uimm",1),("uimm",1)],
    "Ldar": [("reg",1)],
    "Throw": [],
    "Return": [],
    "LdaGlobal": [("uimm",1),("uimm",1)],
    "LdaConstant": [("uimm",1)],
    "CallUndefinedReceiver0": [("reg",1), ("uimm",1)],
    "CallUndefinedReceiver1": [("reg",1), ("reg",1), ("uimm",1)],
    "CallUndefinedReceiver2": [("reg",1), ("reg",1), ("reg",1), ("uimm",1)],
    "GetNamedProperty": [("reg",1), ("uimm",1), ("uimm",1)],
    "LdarZero": [],
    "CallProperty0": [("reg",1), ("reg",1), ("uimm",1)],
    "CallProperty1": [("reg",1), ("reg",1), ("reg",1), ("uimm",1)],
    "CallProperty2": [("reg",1), ("reg",1), ("reg",1),("reg",1), ("uimm",1)],
    "CreateArrayLiteral": [("uimm",1),("uimm",1),("uimm",1)],
    "BitwiseXorSmi": [("uimm",1),("uimm",1)],
    "StaInArrayLiteral": [("reg",1), ("reg",1), ("uimm",1)],
    "LdaSmi": [("uimm",1)],
    "GetIterator": [("reg",1), ("uimm",1),("uimm",1)],
    "LdaFalse": [],
    "LdaTrue": [],
    "LdaTheHole": [],
    "LdaUndefined": [],
    "JumpLoop": [("uimm",1),("uimm",1),("addr", 1)],
    "Jump": [("addr", 1)],
    "JumpIfToBooleanTrue": [("addr", 1)],
    "JumpIfToBooleanFalse": [("addr", 1)],
    "JumpIfTrue": [("addr", 1)],
    "JumpIfFalse": [("addr", 1)],
    "JumpIfJSReceiver": [("addr",1)],
    "CallRuntime": [("skip", 2), ("regdif", 2)], 
    "SetPendingMessage": [],
    "JumpIfUndefinedOrNull": [("addr",1)],
    "TestReferenceEqual": [("reg", 1)],
    "ReThrow": [],
    "Add": [("reg",1),("uimm",1)],
    "TestLessThan": [("reg",1),("uimm",1)],
    "TestEqual": [("reg",1),("uimm",1)],
    "GetKeyedProperty": [("reg",1),("uimm",1)],
}
OPERAND_SPEC_WIDE = {
    "BitwiseXorSmi": [("uimm",2),("uimm",2)],
    "CallProperty0": [("reg",2), ("reg",2), ("uimm",2)],
    "CallProperty1": [("reg",2), ("reg",2),("reg",2), ("uimm",2)],
    "GetNamedProperty": [("reg",2), ("uimm",2), ("uimm",2)],
    "CreateArrayLiteral": [("uimm",2),("uimm",2),("uimm",1)],
    "StaInArrayLiteral": [("reg",2), ("reg",2), ("uimm",2)],
    "Mul": [("reg",2),("uimm",2)],
    "Add": [("reg",2),("uimm",2)],
    "TestEqual": [("reg",2),("uimm",2)],
    "LdaGlobal": [("uimm",2),("uimm",2)],
    "TestLessThan": [("reg",2),("uimm",2)],
    "MulSmi": [("uimm",2),("uimm",2)],
    "AddSmi": [("uimm",2),("uimm",2)],
    "GetKeyedProperty": [("reg",2),("uimm",2)],
    "JumpLoop": [("uimm",2),("uimm",2),("addr",2)],
}

SPECIAL_REGS = {
    0xff: "context",
    0xfe: "closure",
    0x02: "this"
}

INTRINSIC = {
    0x08: "_CreateJSGeneratorObject",
    0x09: "_GeneratorGetResumeMode"
}

def to_regs(v):
    v = v & 0xFF
    if v in SPECIAL_REGS:
        return f"<{SPECIAL_REGS[v]}>"
    if v > 0x80:
        return f"r{0xf9-v}"
    return f"a{v-0x03}"

def read_byte(buf, offset):
    return buf[offset]

def read_signed(buf, offset, length):
    data = buf[offset:offset+length]
    return int.from_bytes(data, byteorder='little', signed=True)

def read_unsigned(buf, offset, length):
    data = buf[offset:offset+length]
    return int.from_bytes(data, byteorder='little', signed=False)

def disasm_bytecode(buf):
    lines = []
    offset = 0
    end = len(buf)
    while offset < end:
        opcode = read_byte(buf, offset)
        is_wide = False
        if opcode == 0:
            opcode = read_byte(buf, offset+1)
            if opcode == 0:
                return lines
            is_wide = True
            offset += 1
        instr_name = BYTECODE_NAMES.get(opcode, f"UNKNOWN_{opcode:#02x}")
        if "UNKNOWN" in instr_name:
            print(instr_name)
            exit(0)
        base_offset = offset
        line = f"{base_offset:04x}: {instr_name}{'.Wide' if is_wide else ''}".ljust(30)

        offset += 1
        
        spec = (OPERAND_SPEC_WIDE if is_wide else OPERAND_SPEC).get(instr_name, None)
        if spec is None:
            print("  ;; no operand spec")
            exit()
        operands = []
        for op_type, length in spec:
            if offset + length > end:
                operands.append(f"?({op_type})")
                offset = end
                break
            if op_type == "reg":
                val = read_unsigned(buf, offset, length)
                operands.append(to_regs(val))
            elif op_type == "regdif":
                assert length == 2
                val1 = read_unsigned(buf, offset, 1)
                val2 = read_unsigned(buf, offset+1, 1)
                if val2 == 0:
                    val2 = 1
                operands.append(f"{to_regs(val1)}-{to_regs(val1-val2+1)}")
            elif op_type == "imm":
                val = read_signed(buf, offset, length)
                operands.append(str(val))
            elif op_type == "uimm":
                val = read_unsigned(buf, offset, length)
                operands.append(str(val))
            elif op_type == "idx":
                val = read_unsigned(buf, offset, length)
                operands.append(f"[idx={val}]")
            elif op_type == "intr":
                val = read_unsigned(buf, offset, length)
                if val not in INTRINSIC:
                    print(f"unknown intrinsic: {hex(val)}")
                    exit()
                operands.append(f"[{INTRINSIC[val]}]")
            elif op_type == "addr":
                val = read_unsigned(buf, offset, length)
                operands.append(f"({base_offset+val:04x})")
            elif op_type == "skip":
                pass
            else:
                val = read_unsigned(buf, offset, length)
                operands.append(f"{op_type}={val}")
            offset += length

        if operands:
            line += " " + ", ".join(operands)
        lines.append(line)
    return lines

if __name__ == "__main__":
    os.system('sqlite3 v8_code_cache_v2 "SELECT hex(data) FROM codecache" | xxd -r -p > ./cache_orig.bin')
    with open("cache_orig.bin", "rb") as f:
        f.read(0x580)
        data = f.read()
    disasm = disasm_bytecode(data)
    # with open("disasm.txt", "w") as f:
    #     f.write("\n".join(disasm))
    
    xor_key = ord('i')
    rarr = []
    for line in disasm:
        for x in re.findall(r"BitwiseXorSmi(.Wide)?\s+(\d+), \d+", line):
            rarr.append(int(x[1])^ xor_key)


    current = 1936
    i = 0
    res = ""
    while current < 2320:
        if "Mul" in disasm[current+3] and "Add" in disasm[current+6]:
            v1 = int(re.findall(r"Ldar\s+r(\d+)", disasm[current+2])[0])-5
            v2 = int(re.findall(r"Mul.Wide\s+r(\d+),", disasm[current+3])[0])-5
            v3 = int(re.findall(r"Ldar\s+r(\d+)", disasm[current+5])[0])-5
            res += chr((rarr[v1] * rarr[v2] + rarr[v3] - 3) // 5)
            current += 8
        elif "Mul" in disasm[current+3] and "Add" in disasm[current+4]:
            v1 = int(re.findall(r"Ldar\s+r(\d+)", disasm[current+2])[0])-5
            v2 = int(re.findall(r"Mul.Wide\s+r(\d+),", disasm[current+3])[0])-5
            v3 = int(re.findall(r"Add.Wide\s+r(\d+)", disasm[current+4])[0])-5
            res += chr((rarr[v1] * rarr[v2] + rarr[v3] - 3) // 5)
            current += 6
        else:
            print(disasm[current:])
            exit()
        i += 1
    print(res)