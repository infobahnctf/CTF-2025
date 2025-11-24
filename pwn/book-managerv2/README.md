# Book Manager V2

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [0xM4hm0ud](https://0xm4hm0ud.me/)                                                          |
| **Category** | pwn                                                                                         |
| **Solves**   | 17                                                                                          |
| **Files**    | [handout.zip](./handout.zip)                                                                |

# Solution

There are no bound checks in create and edit. This gives you an heap overflow vulnerability.

I leaked the heap, because `Move` doesn’t add a null byte. So you can just fill the chunk and leak the next pointer. It can be done from the title field or author field. After leaking you can edit and fix the chunk header.

To get arbitrary read/write, I changed the next pointer to point to the BookPtrs(array in bss that holds the pointer to the chunks). When you have a chunk there, you can put any pointers you want. With that you have arb read/write.

I searched for pointers in the binary that are pointing to the stack. I used that to leak the stack. Then calculated the offset between the stack pointer and rip of the edit function. I then used the arb write primitive to write a rop chain there. I put my final rop chain on the heap because of the size and did a stack pivot to my rop chain.

See [solve.py](solve.py) for the full exploit.
