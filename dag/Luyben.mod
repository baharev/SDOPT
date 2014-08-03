
param Qr := 1432449.0;
param R  := 172.51;
param z0 := 0.0;
param TF0 := 140.0;
param VR := 1200.0;
param N := 18;
param P  := 50.0;

param L := R;

param k10  := 0.1538e4;
param k20  := 0.848e10;
param E1 := 10000;
param E2 := 30000;

param RG := 1.98588;
param Hvap := 250.0;
param Cp := 0.75;
param lambda := -20000.0;
param M := 50.0;

param b1A := -2818.0;
param b2A :=  8.168;
param b1B := -2818.0;
param b2B :=  8.861;
param alpha := 2.0;

param KMT := 10513.0;

########################   VARIABLES   #################################

var V >= L, := L;

var z >=0, <= 1, := 0.5;

var rxt >= 0; # extent_of_reaction

var TR := 140.0; # >= 120.0; # Apparently unbounded variables mess up things

var PR >= P, := P;

var x{1..N+1} >= 0, <=1, := 0.5;

var y{0..N};

var yB >= 0, <=1, := 0.5;

var F0;

var PA;

var PB;

var T1;

def_F0:
  F0 = V - L;

def_PA:
  PA = exp(b1A/(TR+460)+b2A);

def_PB:
  PB = exp(b1B/(TR+460)+b2B);

def_T1:
  T1 = b1B/(log(alpha*P/(1+(alpha-1)*x[1]))-b2B)-460;

extent_of_reaction:
  rxt = k10*exp(-E1/(RG*(TR+460)))*(1-z)-k20*exp(-E2/(RG*(TR+460)))*z;

reactor_material_balance:
  L*x[1] - V*yB + F0*z0 + VR*(rxt) = 0;

reactor_energy_balance:
  F0*TF0 - V*TR + L*T1 - V*Hvap/Cp - (lambda*VR*rxt-Qr)/(M*Cp) = 0;

reactor_pressure:
  PR = PA*(1-z) + PB*z;

reactor_bubble_point:
  yB*PR = PB*z;
  
rate_of_vaporization:
  V = KMT/M*(PR-P);

equilibrium{j in 1..N}:
  y[j] = (alpha*x[j])/(1+(alpha-1)*x[j]);

total_condenser:
  x[N+1] = y[N];

reactor_is_stage_0:
  y[0] = yB;

tray_component_balances{j in 1..N}:
  L*x[j] + V*y[j] = L*x[j+1] + V*y[j-1];

##############   OPTIONS, COMMANDS   ###################################

option show_stats 1;
option presolve 0;
option substout 0;
option var_bounds 2;
option nl_comments 1;
option nl_permute 0;

option auxfiles rc;

write gLuyben;

option solver "/home/ali/ampl/ipopt";
solve;
