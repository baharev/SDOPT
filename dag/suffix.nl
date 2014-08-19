g7 0 1 0 3 20140524 0 1	# problem suffix
 3 3 0 0 3	# vars, constraints, objectives, ranges, eqns
 3 0	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 3 0 0	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0	# discrete variables: binary, integer, nonlinear (b,c,o)
 7 0	# nonzeros in Jacobian, gradients
 5 4	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
S0 2 ivar
1 3
2 4
S0 1 bvar
0 1
S4 2 fvar
1 3.1
2 4.1
S0 1 symvar
1 2
S1 2 icon
1 12
2 13
S1 1 bcon
2 1
S5 2 fcon
1 12.1
2 13.1
S1 1 symcon
1 2
C0	#eq[1]
o5	#^
v0	#x[1]
n2
C1	#eq[2]
o5	#^
v1	#x[2]
n2
C2	#eq[3]
o5	#^
v2	#x[3]
n2
x3	# initial guess
0 0
1 0
2 0
r	#3 ranges (rhs's)
4 3
4 3
4 3
b	#3 bounds (on variables)
3
3
3
k2	#intermediate Jacobian column lengths
1
4
J0 3
0 0
1 1
2 1
J1 2
1 1
2 1
J2 2
1 1
2 1
