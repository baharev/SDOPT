# Artifical upper bounds on the variables, may not be correct in general!!!
param NC := 3;
set C ordered := 1..NC;
set revC ordered by reversed C := C;  
param z{i in C};
param alpha{i in C, j in C};
param B{i in C, j in C};
param tau{i in C, j in C} := B[i,j]/298.15;
param G{i in C, j in C} := exp(-alpha[i,j]*tau[i,j]);
param scale := 1.0e3;

var t >=0, <=1;          # Artifical upper bounds, may not be correct in general
var u >=0, <=1;          # Artifical upper bounds, may not be correct in general
var v{1..NC-1} >=0, <=1; # Artifical upper bounds, may not be correct in general

var x{i in C};
var y{i in C};

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

################################################################################

X{i in 1..NC-1}:
  x[i] = z[i] - t*v[i];
  
XC:
  x[NC] = 1 - sum{i in 1..NC-1} x[i];
  
Y{i in 1..NC-1}:
  y[i] = z[i] + u*v[i];  

YC:
  y[NC] = 1 - sum{i in 1..NC-1} y[i];

################################################################################

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

Norm:
    scale*( sum{i in 1..NC-1} v[i] - (t + u)^2 ) = 0;

################################################################################

data;

param B :=

1 1 0.00
1 2 -124.774
1 3 377.577

2 1 366.098
2 2 0.00
2 3 2839.37

3 1 653.885
3 2 2160.78
3 3 0.00 ;

param alpha :=

1 1 0.00
1 2 0.2950
1 3 0.5856

2 1 0.2950
2 2 0.00
2 3 0.2000

3 1 0.5856
3 2 0.2000
3 3 0.00 ;

param z :=
1 0.2
2 0.4
3 0.4 ;

let v[1] := 0.26319972862483837;
let v[2] := 0.6763287779318519;
let t    := 0.5905371830063607;
let u    := 0.42272674226637325;

