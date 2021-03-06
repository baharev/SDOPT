# Broyden banded 

param N := 16;

var x{1..N} >= -100, <= 101;

con{i in 1..N}:
  5*x[i]^3+2*x[i]+1-sum{j in 1..N: j>=max(1,i-5) and j<=min(N,i+1)} (x[j]^2+x[j]) = 0;

let x[1]  := -0.477446285098725;
let x[2]  := -0.520433482442136;
let x[3]  := -0.558370943009135;
let x[4]  := -0.592117117250195;
let x[5]  := -0.622301248771590;
let x[6]  := -0.650541249094133;
let x[7]  := -0.648055016625447;
let x[8]  := -0.645614708220959;
let x[9]  := -0.643573559963035;
let x[10] := -0.642165324775287;
let x[11] := -0.641534421218548;
let x[12] := -0.641838340629904;
let x[13] := -0.642048212981229;
let x[14] := -0.642138128758668;
let x[15] := -0.643065534204966;
let x[16] := -0.614079591979722;
