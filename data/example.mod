var x; var y; var z :=0.5;

equation: exp(3*x+2*y)+4*z = 1;
  
option show_stats 1;
option solver snopt;
solve;