// With -O, LowerBuiltinCalls turns f.call(...) and f.apply(t, arguments) into a
// fast path guarded by JmpBuiltinIs / JmpBuiltinIsNot (opcode >= 208 in v99).
function add(x, y) { return this.base + x + y; }
function viaCall(f, o) { return f.call(o, 1, 2); }
function viaApply(f) { return f.apply(this, arguments); }
function first() { return "first=" + arguments[1] + "," + arguments[2]; }
var o = { base: 10 };
print(viaCall(add, o));
var fake = { call: function () { return "own call"; } };
print(viaCall(fake, o));
print(viaApply.call(null, first, 2, 3));
