param Lw  := 96.0;
param V_N := 3.0;

param N   := 8;
param N_F := 5;

param  F{1..N} default 0.0;
param  z{1..N} default 0.0;
param qF{1..N} default 0.0;

param alpha := 3.55;
param M1 := 32.04;
param M2 := 60.10;

param x_0{0..N};
param V_0{1..N+1};

#param MS; # for multi start
#param sol{1..5} default 0;
#param failed default 0;
#param tries default 0;

############### VARIABLES ######################################################

var x{j in 0..N} := x_0[j];
var V{j in 1..N+1} >= if j!=(N+1) then V_N-1 else 0, <= V_N+1, := V_0[j];
var L{j in 0..N  };
var HL{j in 0..N};
var B;
var b;
var Q;

var y{j in 1..N+1} = if j==N+1 then 0.0 else (alpha*x[j])/(1.0+(alpha-1.0)*x[j]);

var HV{j in 1..N} = 0.1349*exp(-3.98*x[j])+0.4397*exp(-0.088*x[j]);

cond_comp:
  x[0] = y[1];

def_HL{j in 0..N}:
  HL[j] = 0.1667*exp(-1.087*x[j]);

###############################################################################

x_LB{j in 1..N}: # Only because we want to eliminate x[0]
  x[j] >= 0;
  
x_UB{j in 1..N}:
  x[j] <= 1;
  
L_N_LB:          # we want to keep only L[N]
  L[N] >= -0.1;  # allow infeasibility to see the fifth solution
  
L_N_UB:
  L[N] <= F[N_F];
  
fix_V_N_plus_1:
  V[N+1] = 0;

spec_V_N:
  V[N] = V_N;

###############################################################################
  
def_L_N_minus_1:
  L[N-1] =  L[N] + V[N] - F[N] - V[N+1];
  
def_x_N_minus_1:
  x[N-1] = (L[N]*x[N] + V[N]*y[N] - F[N]*z[N] - V[N+1]*y[N+1]) / L[N-1];
  
def_B:
  B = L[N-1] - V[N];
  
def_b:
  b = L[N-1]*x[N-1] - V[N]*y[N];
  
def_Q:
  Q = L[N-1]*HL[N-1] - V[N]*HV[N];

###############################################################################

total_material_balance{j in (N-2)..0 by -1}:
  L[j] = V[j+1] + B - sum{k in (N-1)..(j+1) by -1} F[k];

component_balance{j in (N-2)..0 by -1}:
  x[j] = (V[j+1]*y[j+1] + b - sum{k in (N-1)..(j+1) by -1} F[k]*z[k]) / L[j];

heat_balance{j in (N-2)..0 by -1}:
  -L[j]*HL[j] + V[j+1]*HV[j+1] + Q - sum{k in (N-1)..(j+1) by -1} qF[k] = 0;

spec_Lw:
  L[0] = Lw/(M1*y[1]+M2*(1.0-y[1]));

################### INITIALIZATION OF THE DATA #################################

data;

param x_0 := 
0  0.999323
1  0.997599
2  0.99207
3  0.97462
4  0.922358
5  0.787479
6  0.710547
7  0.537422
8  0.292755
;

param V_0 := 
1  3.28779
2  3.28632
3  3.28165
4  3.26747
5  3.22876
6  3.19044
7  3.13072
8  3
9  0
;

let L[8] :=  0.706688;

# end of initial estimates
##########################

let  F[N_F] := 1.0;
let  z[N_F] := 0.5;
let qF[N_F] := F[N_F]*0.1667*exp(-1.087*z[N_F]);


###############################################################################

print "Setting options";

option show_stats 1;
option presolve 10;
option substout 1;
option var_bounds 2;
option nl_comments 0;
option nl_permute 0;
option display_precision 0;

option display_precision 0;

option auxfiles rc;

################################################################################

print "Assigning suffixes";

suffix blockid IN, integer;
 
let L[N].blockid := 1;
let x[N].blockid := 1;
 
for {j in 1..N-1}
  let V[j].blockid := N-j+1;

for {j in 1..N-1}
  let x[j].blockid := N-j;

################################################################################

let def_x_N_minus_1.blockid := 1;

for {j in 0..N-2} {
  let component_balance[j].blockid := N-j;
  let heat_balance[j].blockid := N-j;
}

let spec_Lw.blockid := N;

################################################################################

print "Before write command";

write gJacobsenTorn;

print "Done with write";

########################################################################

print "Constraint suffixes missing: ";

for {k in 1.._sncons} { 
  
  if _scon[k].blockid==0 then
  
    print "  ",_sconname[k];
}

print "Variable suffixes missing: ";

for {k in 1.._snvars} {

  if _svar[k].blockid==0 then
  
    print "  ",_svarname[k];
}

end;

print "===========================================";

print "Constraints: ";

for {k in 1.._sncons}
  print _sconname[k],"  ",_scon[k].blockid;
  
print "Variables: ";

for {k in 1.._snvars}
    print _svarname[k],"  ",_svar[k].blockid;


