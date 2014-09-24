g9 0 2 0 3 20140524 0 1 0 1	# problem negate
 3 3 0 0 3	# vars, constraints, objectives, ranges, eqns
 3 0	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 3 0 0	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0	# discrete variables: binary, integer, nonlinear (b,c,o)
 7 0	# nonzeros in Jacobian, gradients
 3 4	# max name lengths: constraints, variables
 0 2 0 1 0	# common exprs: b,c,o,c1,o1
V3 0 0	#x[1]
o1	# - 
n1
o2	#*
v2	#one
v0	#p[1]
V4 0 0	#x[2]
o1	# - 
n1
o2	#*
v2	#one
v1	#p[2]
C0	#Eq1
o44	#exp
o0	# + 
o2	#*
n2
v3	#x[1]
v4	#x[2]
V5 0 2	#x[3]
o16	#-
o54	#sumlist
3
v4	#x[2]
v3	#x[1]
n-1
C1	#Eq2
o54	#sumlist
3
o2	#*
n-2
v4	#x[2]
o16	#-
v3	#x[1]
o2	#*
v5	#x[3]
o44	#exp
v5	#x[3]
C2	#Eq3
o2	#*
v2	#one
o1	# - 
n1
v2	#one
d3	# initial dual guess
0 0
1 0
2 0
x3	# initial guess
0 0.8872045157371093
1 0.6267544694440679
2 1
r	#3 ranges (rhs's)
4 1.82
4 0
4 0
b	#3 bounds (on variables)
0 0 1
0 0 1
0 -2 2
k2	#intermediate Jacobian column lengths
2
4
J0 3
0 0
1 0
2 0
J1 3
0 0
1 0
2 0
J2 1
2 0
