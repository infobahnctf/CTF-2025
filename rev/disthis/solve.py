import builtins
import marshal

# TLDR hook the int function to generate the stringified version of all the expressions being ran.
# From there, you can just brute force each of the individual bytes to recover the final image file.

origs = {}
def hook(orig_fn):
    def wrapper(fn):
        origs[orig_fn] = getattr(builtins, orig_fn, fn)
        setattr(builtins, orig_fn, fn)
        return fn
    return wrapper

class ValList:
    def __init__(self):
        # self.vals = [Int(f"v{i}") for i in range(39944)]
        self.vals = [f"v{i}" for i in range(39944)]

    def __getitem__(self, idx):
        return self.vals[origs['int'](idx.v)]
        # return self.vals[idx]
    
    def __len__(self):
        return len(self.vals)

@hook("open")
class FakeOpen:
    def __init__(self, *args):
        print(f"Opening {args}")
    
    def read(self):
        return ValList()

DEBUG_LOG = 0 
if DEBUG_LOG:
    dprint = print
else:
    dprint = lambda *a, **k: None

CMPS = []

@hook("int")
class FakeInt:
    def __init__(self, *args):
        dprint(f"int{args}")
        if len(args) == 1 and isinstance(args[0], str):
            self.v = args[0]
        else:
            self.v = str(origs['int'](*args))
    
    def __repr__(self):
        return str(self.v)

    def _make(self, expr):
        result = FakeInt.__new__(FakeInt)
        result.v = expr
        return result

    def __add__(self, other):
        dprint(f"__add__: {self.v} + {other}")
        return self._make(f"({self.v} + {other})")

    def __radd__(self, other):
        dprint(f"__radd__: {other} + {self.v}")
        return self._make(f"({other} + {self.v})")

    def __sub__(self, other):
        dprint(f"__sub__: {self.v} - {other}")
        return self._make(f"({self.v} - {other})")

    def __rsub__(self, other):
        dprint(f"__rsub__: {other} - {self.v}")
        return self._make(f"({other} - {self.v})")

    def __mul__(self, other):
        dprint(f"__mul__: {self.v} * {other}")
        return self._make(f"({self.v} * {other})")

    def __rmul__(self, other):
        dprint(f"__rmul__: {other} * {self.v}")
        return self._make(f"({other} * {self.v})")

    def __truediv__(self, other):
        dprint(f"__truediv__: {self.v} / {other}")
        return self._make(f"({self.v} / {other})")

    def __rtruediv__(self, other):
        dprint(f"__rtruediv__: {other} / {self.v}")
        return self._make(f"({other} / {self.v})")

    def __floordiv__(self, other):
        dprint(f"__floordiv__: {self.v} // {other}")
        return self._make(f"({self.v} // {other})")

    def __rfloordiv__(self, other):
        dprint(f"__rfloordiv__: {other} // {self.v}")
        return self._make(f"({other} // {self.v})")

    def __mod__(self, other):
        dprint(f"__mod__: {self.v} % {other}")
        return self._make(f"({self.v} % {other})")

    def __rmod__(self, other):
        dprint(f"__rmod__: {other} % {self.v}")
        return self._make(f"({other} % {self.v})")

    def __pow__(self, other):
        dprint(f"__pow__: {self.v} ** {other}")
        return self._make(f"({self.v} ** {other})")

    def __rpow__(self, other):
        dprint(f"__rpow__: {other} ** {self.v}")
        return self._make(f"({other} ** {self.v})")

    def __eq__(self, other):
        expr = f"{self.v} == {other}"
        CMPS.append(expr)
        # print(expr)
        return True

    def __ne__(self, other):
        dprint(f"__ne__: {self.v} != {other}")
        if other == 39944: return False
        return self._make(f"({self.v} != {other})")

    def __lt__(self, other):
        dprint(f"__lt__: {self.v} < {other}")
        return self._make(f"({self.v} < {other})")

    def __le__(self, other):
        dprint(f"__le__: {self.v} <= {other}")
        return self._make(f"({self.v} <= {other})")

    def __gt__(self, other):
        dprint(f"__gt__: {self.v} > {other}")
        return self._make(f"({self.v} > {other})")

    def __ge__(self, other):
        dprint(f"__ge__: {self.v} >= {other}")
        return self._make(f"({self.v} >= {other})")

    def __neg__(self):
        dprint(f"__neg__: -{self.v}")
        return self._make(f"(-{self.v})")

    def __pos__(self):
        dprint(f"__pos__: +{self.v}")
        return self._make(f"(+{self.v})")

    def __abs__(self):
        dprint(f"__abs__: abs({self.v})")
        return self._make(f"abs({self.v})")

    def __invert__(self):
        dprint(f"__invert__: ~{self.v}")
        return self._make(f"(~{self.v})")

    def __and__(self, other):
        dprint(f"__and__: {self.v} & {other}")
        return self._make(f"({self.v} & {other})")

    def __rand__(self, other):
        dprint(f"__rand__: {other} & {self.v}")
        return self._make(f"({other} & {self.v})")

    def __or__(self, other):
        dprint(f"__or__: {self.v} | {other}")
        return self._make(f"({self.v} | {other})")

    def __ror__(self, other):
        dprint(f"__ror__: {other} | {self.v}")
        return self._make(f"({other} | {self.v})")

    def __xor__(self, other):
        dprint(f"__xor__: {self.v} ^ {other}")
        return self._make(f"({self.v} ^ {other})")

    def __rxor__(self, other):
        dprint(f"__rxor__: {other} ^ {self.v}")
        return self._make(f"({other} ^ {self.v})")

    def __lshift__(self, other):
        dprint(f"__lshift__: {self.v} << {other}")
        return self._make(f"({self.v} << {other})")

    def __rlshift__(self, other):
        dprint(f"__rlshift__: {other} << {self.v}")
        return self._make(f"({other} << {self.v})")

    def __rshift__(self, other):
        dprint(f"__rshift__: {self.v} >> {other}")
        return self._make(f"({self.v} >> {other})")

    def __rrshift__(self, other):
        dprint(f"__rrshift__: {other} >> {self.v}")
        return self._make(f"({other} >> {self.v})")

# we cant just `import output` or else we get errors, so just manually create the code obj
with origs['open']("output.pyc", "rb") as f:
    f.seek(0x10)
    code = f.read()

def dummy():
    pass

code = marshal.loads(code)
dummy.__code__ = code

try:
    # run to collect the expressions
    dummy()
except TypeError:
    pass

print("Solving...")
result = bytearray()
for i, expr in enumerate(CMPS[:39944]):
    print(end=f"\r{i:<5}")
    for guess in range(256):
        globals()[f"v{i}"] = guess
        if eval(expr):
            result.append(guess)
            break
    else:
        exit(f"Failed to find expr on idx {i}")
print()

with origs['open']("flag.png", "wb") as f:
    f.write(result)