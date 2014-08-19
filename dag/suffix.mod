
var x{1..3} := 0.0;

eq{j in 1..3}:
  x[j]^2 + sum{k in 2..3} x[k] = 3;
  
suffix ivar IN integer;
suffix bvar IN binary;
suffix fvar IN;
suffix symvar IN symbolic;

suffix icon IN integer;
suffix bcon IN binary;
suffix fcon IN;
suffix symcon IN symbolic;

option symvar_table '\
  0  non not in the iis\
  1  low at lower bound\
  2  fix fixed\
  3  upp at upper bound\
';

option symcon_table '\
  0  zero   not in the iis\
  1  one   at lower bound\
  2  two   fixed\
  3  three at upper bound\
';

################################################################################

let{i in 2.._nvars} _var[i].ivar := i+1;
let{i in 2.._nvars} _var[i].fvar := (i+1.1);

let _var[1].bvar := 1;
let _var[3].bvar := 0;

let _var[1].symvar := 0;
let _var[2].symvar := 2;

################################################################################

let{i in 2.._ncons} _con[i].icon := i+10;
let{i in 2.._ncons} _con[i].fcon := (i+10.1);

let _con[3].bcon := 1;
let _con[1].bcon := 0;

let _con[1].symcon := 0;
let _con[2].symcon := 2;
  
################################################################################
  
option show_stats 1;
option presolve 0;
option substout 0;
#option var_bounds 2;
option nl_comments 1;
option nl_permute 0;
# option display_precision 0;

# gjh snopt
option solver gjh, auxfiles acefrsu;

write gsuffix;

solve;

display x;

display x.ivar;
display x.bvar;
display x.fvar;
display x.symvar;

display _con.icon;
display _con.bcon;
display _con.fcon;
display _con.symcon;

