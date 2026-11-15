// A switch over 10+ string literals (the minimum in hermesc's SwitchLowering).
// hermesc lowers it to StringSwitchImm, so
// the file header's numStringSwitchImms is non-zero. The 'show source'
// function also makes functionSourceCount non-zero. Both fields sit after
// objShapeTableCount in the v99 header.
function color(name) {
  switch (name) {
    case "red": return 1;
    case "green": return 2;
    case "blue": return 3;
    case "cyan": return 4;
    case "magenta": return 5;
    case "yellow": return 6;
    case "black": return 7;
    case "white": return 8;
    case "orange": return 9;
    case "purple": return 10;
    case "brown": return 11;
    case "gray": return 12;
    default: return -1;
  }
}
function unit(u) {
  switch (u) {
    case "ms": return 1;
    case "s": return 1000;
    case "min": return 60000;
    case "h": return 3600000;
    case "d": return 86400000;
    case "w": return 604800000;
    default: return 0;
  }
}
function shown(a) {
  'show source';
  return a + 1;
}
var names = ["red", "green", "blue", "cyan", "magenta", "yellow", "black", "white", "orange", "purple", "brown", "gray", "pink"];
for (var i = 0; i < names.length; i++) print(names[i], color(names[i]));
print(unit("ms"), unit("h"), unit("w"), unit("x"));
print(shown(41), shown.toString().length > 10);
