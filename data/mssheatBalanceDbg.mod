
# Try tearing: eliminiate x[i,j] with the material
# balance; 
# Use molar flow rates? No, only V[j] remains anyway
# Remains: x[i,N], V[j], T[j], lambda[j]
# Tearing could be done but would make the system
# way too nonlinear

param N   := 3;
param N_F := 2;
param C := 3;
param D := 0.455;
param Vspec := 1.38;

param F{j in 0..N};
param f{i in 1..C, j in 0..N};

param a{1..C};
param b{1..C};
param c{1..C};

param r{1..C, 1..C};
param s{1..C, 1..C};

param P := 100000.0;

param T_L; param T_U;

param hA{1..C};
param hB{1..C};
param hC{1..C};

param HA{1..C};
param HB{1..C};
param Tcrit{1..C};

############### VARIABLES ######################################################

var x{i in 1..C, j in 1..N} >= 0, <= 1, := 1/C;

var V{j in 1..N} >= Vspec*0.5, <= Vspec*1.5;

var lambda{j in 1..N} >= 0, <= 1, := 0.5;

var T{j in 0..N} >= T_L, <= T_U, := 337.0;

var L{j in 0..N} = if j!=N then V[j+1]-D+sum{k in 0..j}F[k] else -D+sum{k in 0..j}F[k];

var K{i in 1..C, j in 1..N};

var z{i in 1..C, j in 1..N};

var y{i in 1..C, j in 1..N};

####### DEFINED VARIABLES #####################################################

var p{i in 1..C, j in 1..N} = exp(a[i]+b[i]/(T[j]+c[i]));

var rcp_T{j in 1..N} = 1.0/T[j];

var Lambda{i1 in 1..C, i2 in 1..C, j in 1..N} = exp(r[i1,i2]+s[i1,i2]*rcp_T[j]);

var sum_xLambda{i in 1..C, j in 1..N} = sum{i1 in 1..C} (x[i1,j]*Lambda[i,i1,j]);

var rcp_sum_xLambda{i in 1..C, j in 1..N} = 1.0/sum_xLambda[i,j];

var gamma{i in 1..C, j in 1..N} =
  exp( -log(sum_xLambda[i,j]) + 1.0 - (sum{i2 in 1..C} (x[i2,j]*Lambda[i2,i,j]*rcp_sum_xLambda[i2,j])) );
  
var hL{i in 1..C, j in 0..N-1} =  10^(-7)*(
    (T[j]^3)*hC[i]/3+(T[j]^2)*hB[i]/2+T[j]*hA[i]-298*hA[i]-44402*hB[i]-8821197.333*hC[i]);
    
var hV{i in 1..C, j in 1..N}   =  10^(-7)*(
    (T[j]^3)*hC[i]/3+(T[j]^2)*hB[i]/2+T[j]*hA[i]-298*hA[i]-44402*hB[i]-8821197.333*hC[i] + 
     HA[i]*(1-T[j]/Tcrit[i])^HB[i]);
  
############## EQUATIONS #######################################################

# TODO Flash calculation to get T[0] instead of fixing it to T_L? 
# hL[i,0] requires T[0]
spec_reflux_temp:
  T[0] = T_L;

spec_reboiler:
  V[N] = Vspec;

def_K{i in 1..C, j in 1..N}:
  K[i,j] = gamma[i,j]*(p[i,j]/P);

def_y{i in 1..C, j in 1..N}:
  y[i,j] = K[i,j]*x[i,j];
  
def_z{i in 1..C, j in 1..N}:
  z[i,j] = x[i,j]*(lambda[j]+(1-lambda[j])*K[i,j]);
  
sum_y_minus_sum_x{j in 1..N}:
  sum{i in 1..C} (((K[i,j]-1)*z[i,j])/(lambda[j]+(1-lambda[j])*K[i,j]))= 0;

sum_z{j in 1..N}:
  sum{i in 1..C} z[i,j] - 1.0 = 0.0;
  
M_eq{i in 1..C, j in 1..N}:
  L[j-1]*( if j!=1 then x[i,j-1] else y[i,1]) + f[i,j] + 
  ( if j!=N then V[j+1]*y[i,j+1] else 0.0) - L[j]*x[i,j] - V[j]*(y[i,j]) = 0.0;

H_eq{j in 1..N-1}:
  (L[j-1]*(sum{i in 1..C}(if j!=1 then x[i,j-1] else y[i,1])*hL[i,j-1]))
  + sum{i in 1..C} f[i,j]*hL[i,j] + 
   V[j+1]*(sum{i in 1..C} y[i,j+1]*hV[i,j+1])
    -L[j]*(sum{i in 1..C} x[i,j]*hL[i,j] )-V[j]*( sum{i in 1..C} y[i,j]*hV[i,j] ) = 0.0;  
 
################### DATA SECTION ###############################################

data;

param hA := 
1   105800.0
2   102930.0
3   140140.0;

param hB := 
1   -362.23
2    129.1
3   -152.3;

param hC := 
1   0.9379
2   0.62516
3   0.695;

param HA := 
1   52390000   
2   53781000
3   49507000
;

param HB := 
1   0.36820
2   0.39523
3   0.37742
;

param Tcrit := 
1   512.64
2   554.5
3   591.79
;

let a[1] := 23.4832;
let a[2] := 20.5110;
let a[3] := 20.9064;

let b[1] := -3634.01;
let b[2] := -2664.30;
let b[3] := -3096.52;

let c[1] := -33.768;
let c[2] := -79.483;
let c[3] := -53.668;

let r[1,2] :=  0.7411;
let r[1,3] :=  0.9645;
let r[2,3] := -1.4350;

let r[2,1] := -1.0250;
let r[3,1] := -0.9645;
let r[3,2] :=  2.7470;

let r[1,1] := 0.0;
let r[2,2] := 0.0;
let r[3,3] := 0.0;

let s[1,2] := -477.00;
let s[1,3] := -903.1024;
let s[2,3] :=  768.20;

let s[2,1] :=  72.78;
let s[3,1] := -140.9995;
let s[3,2] := -1419.0;

let s[1,1] := 0.0;
let s[2,2] := 0.0;
let s[3,3] := 0.0;

# THESE BOUNDS WERE CALCULATED IN ADVANCE

let T_L := 336.3;
let T_U := 383.4;

# FEED VALUES, LOCATION

for {i in 1..C, j in 0..N}
	let f[i,j] := 0.0;

let f[1, N_F] := 0.4098370;
let f[2, N_F] := 0.01229769;
let f[3, N_F] := 0.06090665;

for {j in 0..N}
	let F[j] := sum{i in 1..C} f[i,j];

################################################################################

# solve;
