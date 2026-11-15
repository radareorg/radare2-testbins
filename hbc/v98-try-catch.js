// Exception handlers: catch, finally, nested, rethrow, finally-with-return,
// catch inside a loop with break/continue.
function basic(x) {
  try { if (x < 0) throw new Error("neg"); return "ok" + x; }
  catch (e) { return "caught:" + e.message; }
}
function withFinally(x) {
  var log = [];
  try { log.push("t"); if (x) throw x; log.push("t2"); }
  catch (e) { log.push("c" + e); }
  finally { log.push("f"); }
  return log.join(",");
}
function nested(x) {
  var r = "";
  try {
    try { if (x === 1) throw "inner"; r += "i"; }
    catch (e) { r += "ci"; if (x === 1) throw "rethrown"; }
    finally { r += "fi"; }
    if (x === 2) throw "outer";
    r += "o";
  } catch (e2) { r += "co(" + e2 + ")"; }
  return r;
}
function finallyReturn() { try { return "try"; } finally { print("finally ran"); } }
function loopCatch(n) {
  var s = 0;
  for (var i = 0; i < n; i++) {
    try { if (i % 3 === 0) throw i; if (i === 7) break; s += i; }
    catch (e) { s += 100; continue; }
    finally { s += 1000; }
  }
  return s;
}
print(basic(1)); print(basic(-1));
print(withFinally(0)); print(withFinally("X"));
print(nested(0)); print(nested(1)); print(nested(2));
print(finallyReturn());
print(loopCatch(10));
