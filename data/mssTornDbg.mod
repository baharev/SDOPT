
# NUMBER OF STAGES
param N := 3;

# FEED STAGE LOCATION
param N_F := 2;

# NUMBER OF COMPONENTS
param C := 3;

# DISTILLATE MOLAR FLOW RATE
param D;

let D := 0.455;

# VAPOR FLOW RATE, FROM SPECIFICATION
param V := 1.38;

# FEED LOCATION AND VALUES ARE GIVEN IN THE DATA SECTION

param F{j in 0..N};
param f{i in 1..C, j in 0..N};

# AUXILIARY PARAMETERS

param L{j in 0..N};
param B := F[N_F] - D;

################## PARAMETERS ##################################################

param a{1..C};
param b{1..C};
param c{1..C};

param r{1..C, 1..C};
param s{1..C, 1..C};

param P := 100000.0;

# LOWER/UPPER BOUNDS ON THE VARIABLES, INITIAL ESTIMATES (IF NEEDED)
# VALUES ARE GIVEN IN THE DATA SECTION

param x_L{1..C, 1..N}; param x_U{1..C, 1..N}; param x_0{1..C, 1..N};

param T_0{1..N};

############### VARIABLES ######################################################

var x{i in 1..C, j in 1..N} >= x_L[i,j], <= x_U[i,j], := x_0[i,j];

var T{j in 1..N} >= 336.3, <= 383.4, := T_0[j];

####### DEFINED VARIABLES (THEY ARE ELIMINATED BY PRESOLVE / SUBTITUTION) ######

var p{i in 1..C, j in 1..N} = exp(a[i]+b[i]/(T[j]+c[i]));

var rcp_T{j in 1..N} = 1.0/T[j];

var Lambda{i1 in 1..C, i2 in 1..C, j in 1..N} = exp(r[i1,i2]+s[i1,i2]*rcp_T[j]);

var sum_xLambda{i in 1..C, j in 1..N} = sum{i1 in 1..C} (x[i1,j]*Lambda[i,i1,j]);

var rcp_sum_xLambda{i in 1..C, j in 1..N} = 1.0/sum_xLambda[i,j];

var gamma{i in 1..C, j in 1..N} =
  exp( -log(sum_xLambda[i,j]) + 1.0 - (sum{i2 in 1..C} (x[i2,j]*Lambda[i2,i,j]*rcp_sum_xLambda[i2,j])) );

var K{i in 1..C, j in 1..N} = gamma[i,j]*(p[i,j]/P);

var y{i in 1..C, j in 1..N} = K[i,j]*x[i,j];
  
############## EQUATIONS #######################################################

M_eq{j in 1..N-1, i in 1..C}:
	L[j]*x[i,j] + sum{i1 in j+1..N} f[i,i1] - B*x[i,N] - V*y[i,j+1] = 0.0;

S_x_eq{j in 1..N}:
	sum{i in 1..C} x[i,j] - 1.0 = 0.0;

M_tot{i in 1..C}:
	D*y[i,1] + B*x[i,N] - f[i,N_F] = 0.0;

################### DATA SECTION ###############################################

data;

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

# LOWER AND UPPER BOUNDS ON THE VARIABLES

for {j in 1..N} {
	let x_L[1,j] := 0.0;
	let x_U[1,j] := 0.9998;
	let x_L[2,j] := 1.0e-4;
	let x_U[2,j] := 0.9999;
	let x_L[3,j] := 1.0e-4;
	let x_U[3,j] := 0.9999;
}

# THIS BOUND SEEMS TO BE REASONABLE FROM ENGINEENERING POINT OF VIEW

let x_L[1,1] := 0.83;

# FEED VALUES, LOCATION

for {i in 1..C, j in 0..N}
	let f[i,j] := 0.0;

let f[1, N_F] := 0.4098370;
let f[2, N_F] := 0.01229769;
let f[3, N_F] := 0.06090665;

for {j in 0..N}
	let F[j] := sum{i in 1..C} f[i,j];

for {j in 0..N}
  let L[j] := if (j!=N) then V-D+sum{k in 0..j}F[k] else  -D+sum{k in 0..j}F[k];

################################################################################

# DUMB INITIAL ESTIMATES (IF NEEDED)

for {i in 1..C, j in 1..N}
	let x_0[i,j] := 0.33;

for {j in 1..N}
	let T_0[j] := 337.0;

################################################################################

suffix blockid IN, integer;

for {i in 1..C}
  let x[i,N].blockid   := 1;

for {i in 1..C, j in 1..N} {
  if j!=1 then 
    let x[i,j-1].blockid := N-j+1;
  let T[j].blockid       := N-j+1;
}

################################################################################

let S_x_eq[N].blockid := 1;

for {i in 1..C, j in 2..N} {
  let M_eq[j-1,i].blockid := N-j+1;   
  let S_x_eq[j-1].blockid := N-j+1;
}

for {i in 1..C}
  let M_tot[i].blockid := N;

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

###############################################################################

solve;

