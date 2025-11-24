# very-safe-pickle

|              |                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------- |
| **CTF**      | [Infobahn CTF 2025](http://2025.infobahnc.tf/) [(CTFtime)](https://ctftime.org/event/2878/) |
| **Author**   | [t-chen](https://github.com/tepel-chen/)                                                    |
| **Category** | jail                                                                                        |
| **Solves**   | 13                                                                                          |
| **Files**    | [very-safe-pickle.zip](./very-safe-pickle.zip)                                              |

# Solution

At first glance, it seems we cannot invoke a method or create a class instance due to the forbidden opcodes. However, we can use the `BUILD` opcode, which performs the following actions:

```python
def load_build(self):
    stack = self.stack
    state = stack.pop()
    inst = stack[-1]
    setstate = getattr(inst, "__setstate__", _NoValue)
    if setstate is not _NoValue:
        setstate(state)
        return
    slotstate = None
    if isinstance(state, tuple) and len(state) == 2:
        state, slotstate = state
    if state:
        inst_dict = inst.__dict__
        intern = sys.intern
        for k, v in state.items():
            if type(k) is str:
                inst_dict[intern(k)] = v
            else:
                inst_dict[k] = v
    if slotstate:
        for k, v in slotstate.items():
            setattr(inst, k, v)
```

This allows us to overwrite an object's `__dict__`, including its magic methods. The [`__getattr__` magic method](https://docs.python.org/3/reference/datamodel.html#object.__getattr__) works like this:

```python
import enum

def f(arg):
    print('f is called with:', arg)

enum.__dict__["__getattr__"] = f
getattr(enum, 'foobar') # prints "f is called with: foobar"
```

Since the [`GLOBAL` opcode also uses `getattr`](https://github.com/python/cpython/blob/432432bfc8a2a2cc99d8037fb6a83c977d9eb663/Lib/pickle.py#L1701) when importing values from a module, overriding this method will allow us to hijack the import process and invoke arbitrary functions.

We cannot directly import modules like `os`, `subprocess`, `posix`, or `builtins` because their names contain the prohibited bytes `o` or `i`. Instead, we can first import `html.unescape` and use it to create arbitrary strings from their HTML-encoded representations. Then, we can use the `STACK_GLOBAL` opcode, which imports modules using strings from the stack.

Here are the steps to solve this challenge:

1. Import `unescape` from the `html` module.
2. Import `enum` from the `re` module, and use the `BUILD` opcode to overwrite its `__getattr__` method with `unescape`.
3. Attempt to import `&#98;&#117;&#105;&#108;&#116;&#105;&#110;&#115;` from the `enum` module. This triggers our hijacked `__getattr__`, which is `unescape`. This decodes the HTML entity into the string `builtins` and pushes it onto the stack.
4. Use the `STACK_GLOBAL` opcode to import `eval` from the `builtins` module, whose name is now on the stack.
5. Import `_types` from the `ctypes` module and use the `BUILD` opcode to overwrite its `__getattr__` method with `eval`.
6. Attempt to import an HTML-encoded RCE payload from the `enum` module. This again calls `unescape`, which decodes the payload and pushes the resulting RCE command string onto the stack.
7. Use the `STACK_GLOBAL` opcode to import the RCE string from the `types` module. This triggers the hijacked `__getattr__` (which is now `eval`), executing our RCE payload.

(`re.enum` and `ctypes._types` can be replaced with any module that is a submodule of another, as long as their names do not contain forbidden characters and is written in Python, not C.)

See [solve.py](./solve.py) for the full exploit code.
