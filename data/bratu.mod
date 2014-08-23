
param n := 5;

param c := (1.0/(n+1.0))^2;

var x{0..n+1} := 3; # intial guesses: 3 and 2.5

x_LB{i in 1..n}:
  x[i] >=0;
  
x_UB{i in 1..n}:
  x[i] <=5;

def_x0:
  x[0] = 0;
  
def_last:
  x[n+1] = 0;
  
eq{i in 1..n}:
  x[i+1] - 2*x[i] + x[i-1] + c*exp(x[i]) = 0.0;

option presolve 10;
option substout 0;

option show_stats 1;

option solver "/home/ali/ampl/ipopt";
solve;

