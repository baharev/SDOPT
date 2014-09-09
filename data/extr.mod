
################## PARAMETERS FROM SPECIFICATION ###############################

# NUMBER OF STAGES
param N := 16;

# FEED STAGE LOCATIONS
param N_F1 := 5;
param N_F2 := 11;

# NUMBER OF COMPONENTS
param C := 3;

# REFLUX RATIO
param R := 5.0;

# DISTILLATE MOLAR FLOW RATE
param D := 0.73;

# PURITY RESTRICTION ON THE DISTILLATE COMPOSITION
param x_acetone_min := 0.92;

# LOWER BOUND ON ALL MOL FRACTIONS IN THE ENTIRE COLUMN
param xmin := 0.001;

################## PARAMETERS ##################################################

# FEED LOCATIONS AND VALUES ARE GIVEN IN THE DATA SECTION

param F{j in 0..N};
param f{i in 1..C, j in 0..N};

# FURTHER MODEL PARAMETERS

param lambda{1..C};
param a{1..C};
param b{1..C};
param c{1..C};
param Vm{1..C};
param k{1..C, 1..C};

param RG := 1.98721;
param P := 760.0;

# LOWER/UPPER BOUNDS ON THE VARIABLES, INITIAL ESTIMATES (IF NEEDED)
# VALUES ARE GIVEN IN THE DATA SECTION

param x_L{1..C, 0..N};   param x_U{1..C, 0..N};   param x_0{1..C, 0..N};
param y_L{1..C, 1..N+1}; param y_U{1..C, 1..N+1}; param y_0{1..C, 1..N+1};
param K_L{1..C, 1..N};   param K_U{1..C, 1..N};   param K_0{1..C, 1..N};

param V_L{1..N+1} default (1-0.32)*(R+1)*D;
param V_U{1..N+1} default (1+0.32)*(R+1)*D;
param V_0{1..N+1};

param l_L{1..C, 0..N}; param l_U{1..C, 0..N}; param l_0{1..C, 0..N};

param v_L{1..C, 1..N+1};
param v_U{1..C, j in 1..N+1} default V_U[j];
param v_0{1..C, 1..N+1};

param T_0{1..N};
param Q_L;	param Q_U;	param Q_0;

############### VARIABLES ######################################################

var x{i in 1..C, j in 0..N  } >= x_L[i,j], <= x_U[i,j], := x_0[i,j];

var y{i in 1..C, j in 1..N+1} >= y_L[i,j], <= y_U[i,j], := y_0[i,j];

var K{i in 1..C, j in 1..N  } >= K_L[i,j], <= K_U[i,j], := K_0[i,j];

var V{j in 1..N+1} >= V_L[j], <= V_U[j], := V_0[j];

var v{i in 1..C, j in 1..N+1} >= v_L[i,j], <= v_U[i,j], := v_0[i,j];

var l{i in 1..C, j in 0..N  } >= l_L[i,j], <= l_U[i,j], := l_0[i,j];

var Q >= Q_L, <= Q_U, := Q_0;

var T{j in 1..N} >= 327.0, <= 374.0, := T_0[j];

####### DEFINED VARIABLES (THEY ARE ELIMINATED BY PRESOLVE / SUBTITUTION) ######

var L{j in 0..N} = V[j+1] - D + sum{i1 in 0..j} F[i1];

var H{j in 1..N+1} = sum{i in 1..C} lambda[i]*y[i,j];

var rcp_T{j in 1..N} = 1.0/T[j];

var p{i in 1..C, j in 1..N} = exp(a[i]-b[i]/(T[j]+c[i]));

var Lambda{i1 in 1..C, i2 in 1..C, j in 1..N} =
  Vm[i2]/Vm[i1]*exp((-k[i1,i2]/RG)*rcp_T[j]);

var sum_xLambda{i in 1..C, j in 1..N} = sum{i1 in 1..C} (x[i1,j]*Lambda[i,i1,j]);

var rcp_sum_xLambda{i in 1..C, j in 1..N} = 1.0/sum_xLambda[i,j];

var gamma{i in 1..C, j in 1..N} =
  exp( -log(sum_xLambda[i,j]) + 1.0 - (sum{i2 in 1..C} (x[i2,j]*Lambda[i2,i,j]*rcp_sum_xLambda[i2,j])) );
  
############## EQUATIONS #######################################################

M_aux_y1_x0{i in 1..C}:
	x[i,0] - y[i,1] = 0.0;

M_aux_yNp1_xN{i in 1..C}:
	y[i,N+1] - x[i,N] = 0.0;
	
M_aux_V1:
	V[1] - (R+1.0)*D = 0.0;
	
M_aux_l{i in 1..C, j in 0..N}:
	l[i,j] - L[j]*x[i,j] = 0.0;

M_aux_v{i in 1..C, j in 1..N+1}:
	v[i,j] - V[j]*y[i,j] = 0.0;

M_eq{i in 1..C-1, j in 1..N}:
	l[i,j] + D*y[i,1] - v[i,j+1] - sum{i1 in 1..j} f[i,i1] = 0.0;

E_eq{i in 1..C, j in 1..N}:
	y[i,j] - K[i,j]*x[i,j] = 0.0;
	
S_x_eq{j in 1..N}:
	sum{i in 1..C} x[i,j] - 1.0 = 0.0;

S_y_eq{j in 1..N}:
	sum{i in 1..C} y[i,j] - 1.0 = 0.0;

H_eq{j in 1..N+1}:
	Q - V[j]*H[j] = 0.0;

E_aux_K{i in 1..C, j in 1..N}:
	K[i,j] - gamma[i,j]*(p[i,j]/P) = 0.0;

################### DATA SECTION ###############################################
	
data;

let lambda[1] := 6.960;
let lambda[2] := 8.426;
let lambda[3] := 9.717;

let a[1] := 16.732;
let a[2] := 18.510;
let a[3] := 18.304;

let b[1] := 2975.9;
let b[2] := 3593.4;
let b[3] := 3816.4;

let c[1] := -34.523;
let c[2] := -35.225;
let c[3] := -46.130;

let Vm[1] := 74.050;
let Vm[2] := 40.729;
let Vm[3] := 18.069;

for {i in 1..C, j in 0..N} {

	let x_L[i,j] := xmin;
	let x_U[i,j] := 1.0-(C-1)*xmin;
}

for {i in 1..C, j in 1..N+1} {
	
	let y_L[i,j] := xmin;
	let y_U[i,j] := 1.0-(C-1)*xmin;
}

let y_L[1,1] := x_acetone_min;
let y_U[2,1] := 1.00-y_L[1,1]-y_L[3,1];
let y_U[3,1] := 1.00-y_L[1,1]-y_L[2,1];

let x_L[1,0] := y_L[1,1];
let x_U[2,0] := y_U[2,1];
let x_U[3,0] := y_U[3,1];

for {j in 1..N} {
	let K_L[1,j] := 0.98;
	let K_U[1,j] := 38.97;
	let K_L[2,j] := 0.80;
	let K_U[2,j] := 7.53;
	let K_L[3,j] := 0.26;
	let K_U[3,j] := 1.01;
}

let Q_L := (R+1)*D*min(lambda[1], lambda[2], lambda[3]);
let Q_U := (R+1)*D*max(lambda[1], lambda[2], lambda[3]);

for {i in 1..C, j in 0..N}
	let f[i,j] := 0.0;

let f[3, N_F1] := 2.000;

let f[1, N_F2] := 0.783;
let f[2, N_F2] := 0.217;

for {j in 0..N}
	let F[j] := sum{i in 1..C} f[i,j];

for {i in 1..C, j in 1..N+1}
	let v_L[i,j] := 0.0;

for {i in 1..C, j in 0..N}
	let l_L[i,j] := 0.0;

for {i in 1..C, j in 0..N}
	let l_U[i,j] := sum{i1 in 0..j} f[i,i1] + v_U[i,j+1] - y_L[i,1]*D;

let k[1,2] := -157.981;
let k[1,3] :=  393.27;
let k[2,3] := -52.605;

let k[2,1] := 592.638;
let k[3,1] := 1430.0;
let k[3,2] := 620.63;

let k[1,1] := 0.0;
let k[2,2] := 0.0;
let k[3,3] := 0.0;

# DUMB INITIAL ESTIMATES (IF NEEDED)
	
for {i in 1..C, j in 0..N}
	let x_0[i,j] := (x_L[i,j]+x_U[i,j])/2.0;

for {i in 1..C, j in 1..N+1}
	let y_0[i,j] := (y_L[i,j]+y_U[i,j])/2.0;
	
for {i in 1..C, j in 1..N+1}
	let v_0[i,j] := (v_L[i,j]+v_U[i,j])/2.0;
	
for {i in 1..C, j in 0..N}
	let l_0[i,j] := (l_L[i,j]+l_U[i,j])/2.0;

for {i in 1..C, j in 1..N}
	let K_0[i,j] := (K_L[i,j]+K_U[i,j])/2.0;
	
for {j in 1..N+1}
	let V_0[j] := (V_L[j]+V_U[j])/2.0;
	
for {j in 1..N}
	let T_0[j] := 335.0;

let Q_0 := (Q_L + Q_U)/2.0;

################################################################################

solve;
