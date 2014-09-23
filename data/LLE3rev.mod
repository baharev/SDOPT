set C ordered := 1..3;
set revC ordered by reversed C := C;  
param z{i in C};
param alpha{i in C, j in C};
param tau{i in C, j in C};
param G{i in C, j in C} = exp(-alpha[i,j]*tau[i,j]);
param scale := 1.0e3;

var lambda >= 0, <= 1;
var x{i in C} >= 0, <= 1;
var y{i in C} >= 0, <= 1;

var sum_Gx{i in C};
var sum_tauGx{i in C};
var px{i in C};
var qx{i in C};
var rx{i in C};
var sx{i in C};
var ln_gx{i in C};

var sum_Gy{i in C};
var sum_tauGy{i in C};
var py{i in C};
var qy{i in C};
var ry{i in C};
var sy{i in C};
var ln_gy{i in C};

###################################################################################

Sum_Gx{j in C}:
    sum_Gx[j] = sum{i in C} G[i,j]*x[i];

Px{i in C}:
    px[i] = 1/sum_Gx[i];
    
Qx{i in C}:
    qx[i] = px[i]*x[i];    
    
Sum_tauGx{j in C}:
    sum_tauGx[j] = sum{i in C} tau[i,j]*G[i,j]*x[i];
    
Rx{i in C}:
    rx[i] = sum_tauGx[i]*px[i];

Sx{i in C}:
    sx[i] = qx[i]*rx[i];
    
Ln_gx{i in C}:
    ln_gx[i] = rx[i] + sum{j in C} tau[i,j]*G[i,j]*qx[j] - sum{j in C} G[i,j]*sx[j];    

####################################################################################
    
Sum_Gy{j in C}:
    sum_Gy[j] = sum{i in C} G[i,j]*y[i];
    
Py{i in C}:
    py[i] = 1/sum_Gy[i];
    
Qy{i in C}:
    qy[i] = py[i]*y[i];    

Sum_tauGy{j in C}:
    sum_tauGy[j] = sum{i in C} tau[i,j]*G[i,j]*y[i];

Ry{i in C}:
    ry[i] = sum_tauGy[i]*py[i];
    
Sy{i in C}:
    sy[i] = qy[i]*ry[i];
    
Ln_gy{i in C}:
    ln_gy[i] = ry[i] + sum{j in C} tau[i,j]*G[i,j]*qy[j] - sum{j in C} G[i,j]*sy[j];
    
####################################################################################    
    
Equilibrium{i in revC}:
	scale*(ln_gx[i] + log(x[i]) - ln_gy[i] - log(y[i])) = 0;

Material_balance{i in 1 .. 2}:
	scale*(lambda*x[i] + (1-lambda)*y[i] - z[i]) = 0;
	
Sum_y:
	sum{i in C} scale*y[i] - scale = 0;	
	
Sum_x:
	sum{i in C} scale*x[i] - scale = 0;
	
# Cut off trivial solution:
#trival:
#	x[2] <= 0.047;
#trival:
#    y[3] >= 0.83;
	
################################################################################

data;

param alpha :=

1 1 0.00
1 2 0.30
1 3 0.30

2 1 0.30
2 2 0.00
2 3 0.48

3 1 0.30
3 2 0.48
3 3 0.00 ;

param tau :=

1 1  0.00000
1 2 -0.61259
1 3 -0.07149

2 1  0.71640
2 2  0.00000
2 3  0.90047

3 1  2.74250
3 2  3.51307 
3 3  0.00000;

# param z :=
# 1 0.148
# 2 0.052
# 3 0.800 ;
# 
# let x[1] := 0.1545;
# let x[2] := 0.0550;
# let x[3] := 0.7905;
# let y[1] := 0.1166;
# let y[2] := 0.0373;
# let y[3] := 0.8461;
# let lambda := 0.72;

param z :=
1 0.12
2 0.08
3 0.80 ;

let x[1] := 0.063945;
let x[2] := 0.030845;
let x[3] := 0.90521;
let y[1] := 0.14755;
let y[2] := 0.10416;
let y[3] := 0.74830;
let lambda := 0.32950;

options ipopt_options "acceptable_tol=1.0e-14";
