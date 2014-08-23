
param n := 6;

# bounds are valid till n < 3000

var x{1..n} >= -10, <= 10;

var z{i in 1..n} >= -10*(n-i+1), <= 10*(n-i+1);

cubic{i in 1..n}:
  2.5*x[i]^3 - 10.5*x[i]^2 + 11.8*x[i] + z[1] - i = 0;
  
recursion{i in 1..n}:
  (if i<n-1 then z[i+1]) - z[i] + x[i] = 0;
  
option show_stats 1;
option presolve 0;
option substout 0;

option solver "/home/ali/ampl/ipopt";
solve;