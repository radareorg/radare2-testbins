// One comparison per function, each returning constants, so the decompiled
// output has no data flow to get wrong: only the operator can be wrong.
// In v99, ===/!==/==/!= compile to JStrictEqual(212)/JStrictNotEqual(214)/
// JEqual(208)/JNotEqual(210), opcodes a v98 table misreads.
function seq(a, b) { if (a === b) return 'T'; return 'f'; }
function nseq(a, b) { if (!(a === b)) return 'T'; return 'f'; }
function sne(a, b) { if (a !== b) return 'T'; return 'f'; }
function nsne(a, b) { if (!(a !== b)) return 'T'; return 'f'; }
function eq(a, b) { if (a == b) return 'T'; return 'f'; }
function neq(a, b) { if (!(a == b)) return 'T'; return 'f'; }
function ne(a, b) { if (a != b) return 'T'; return 'f'; }
function nne(a, b) { if (!(a != b)) return 'T'; return 'f'; }
function lt(a, b) { if (a < b) return 'T'; return 'f'; }
function nlt(a, b) { if (!(a < b)) return 'T'; return 'f'; }
function le(a, b) { if (a <= b) return 'T'; return 'f'; }
function nle(a, b) { if (!(a <= b)) return 'T'; return 'f'; }
function gt(a, b) { if (a > b) return 'T'; return 'f'; }
function ngt(a, b) { if (!(a > b)) return 'T'; return 'f'; }
function ge(a, b) { if (a >= b) return 'T'; return 'f'; }
function nge(a, b) { if (!(a >= b)) return 'T'; return 'f'; }
function isNull(a) { if (a === null) return 'T'; return 'f'; }
function notUndef(a) { if (a !== undefined) return 'T'; return 'f'; }
function looseNull(a) { if (a == null) return 'T'; return 'f'; }
function isZero(a) { if (a === 0) return 'T'; return 'f'; }
function isFn(a) { if (typeof a === 'function') return 'T'; return 'f'; }
var fs = [seq, nseq, sne, nsne, eq, neq, ne, nne, lt, nlt, le, nle, gt, ngt, ge, nge];
var unary = [isNull, notUndef, looseNull, isZero, isFn];
var pairs = [[1, 2], [2, 2], [3, 2], [1, '1'], [null, undefined], [NaN, NaN], ['a', 'b']];
for (var i = 0; i < fs.length; i++) { var s = fs[i].name + ' '; for (var j = 0; j < pairs.length; j++) s += fs[i](pairs[j][0], pairs[j][1]); print(s); }
var vals = [null, undefined, 0, '', print];
for (var i = 0; i < unary.length; i++) { var s = unary[i].name + ' '; for (var j = 0; j < vals.length; j++) s += unary[i](vals[j]); print(s); }
