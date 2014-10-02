var p{1..2} >= 0, <= 1;
var one >= -2, <= 2;
var x{1..3};

X{i in 1..2}:
  x[i] = 1 - one*p[i];

X3:
  x[3] = 1 - sum{i in 1..2} x[i];

Eq1:
  exp(2*x[1] + x[2]) = 1.82;
  
Eq2:
  x[3]*exp(x[3]) = x[1] + 2*x[2];
  
Eq3:
  one*(1-one) = 0;

let p[1] := 0.8872045157371093;
let p[2] := 0.6267544694440679;
let one  := 1; 
