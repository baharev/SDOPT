g7 0 2 0 48 20140224 0 1	# problem Luyben
 48 48 0 0 48	# vars, constraints, objectives, ranges, eqns
 44 0	# nonlinear constraints, objectives
 0 0	# network constraints: nonlinear, linear
 44 0 0	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 0 0 0 0	# discrete variables: binary, integer, nonlinear (b,c,o)
 160 0	# nonzeros in Jacobian, gradients
 27 5	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
C0	#def_F0
n0
C1	#def_PA
o16	#-
o44	#exp
o0	# + 
o3	#/
n-2818
o0	# + 
v3	#TR
n460
n8.168
C2	#def_PB
o16	#-
o44	#exp
o0	# + 
o3	#/
n-2818
o0	# + 
v3	#TR
n460
n8.861
C3	#def_T1
o16	#-
o3	#/
n-2818
o1	# - 
o43	#log
o3	#/
n100
o0	# + 
v5	#x[1]
n1
n8.861
C4	#extent_of_reaction
o1	# - 
o2	#*
o2	#*
n8.48e+09
o44	#exp
o16	#-
o3	#/
n30000
o2	#*
n1.98588
o0	# + 
v3	#TR
n460
v1	#z
o2	#*
o2	#*
n1538
o44	#exp
o16	#-
o3	#/
n10000
o2	#*
n1.98588
o0	# + 
v3	#TR
n460
o1	# - 
n1
v1	#z
C5	#reactor_material_balance
o16	#-
o2	#*
v0	#V
v43	#yB
C6	#reactor_energy_balance
o16	#-
o2	#*
v0	#V
v3	#TR
C7	#reactor_pressure
o1	# - 
o16	#-
o2	#*
v46	#PB
v1	#z
o2	#*
v45	#PA
o1	# - 
n1
v1	#z
C8	#reactor_bubble_point
o1	# - 
o2	#*
v43	#yB
v4	#PR
o2	#*
v46	#PB
v1	#z
C9	#rate_of_vaporization
n0
C10	#equilibrium[1]
o16	#-
o3	#/
o2	#*
n2
v5	#x[1]
o0	# + 
v5	#x[1]
n1
C11	#equilibrium[2]
o16	#-
o3	#/
o2	#*
n2
v6	#x[2]
o0	# + 
v6	#x[2]
n1
C12	#equilibrium[3]
o16	#-
o3	#/
o2	#*
n2
v7	#x[3]
o0	# + 
v7	#x[3]
n1
C13	#equilibrium[4]
o16	#-
o3	#/
o2	#*
n2
v8	#x[4]
o0	# + 
v8	#x[4]
n1
C14	#equilibrium[5]
o16	#-
o3	#/
o2	#*
n2
v9	#x[5]
o0	# + 
v9	#x[5]
n1
C15	#equilibrium[6]
o16	#-
o3	#/
o2	#*
n2
v10	#x[6]
o0	# + 
v10	#x[6]
n1
C16	#equilibrium[7]
o16	#-
o3	#/
o2	#*
n2
v11	#x[7]
o0	# + 
v11	#x[7]
n1
C17	#equilibrium[8]
o16	#-
o3	#/
o2	#*
n2
v12	#x[8]
o0	# + 
v12	#x[8]
n1
C18	#equilibrium[9]
o16	#-
o3	#/
o2	#*
n2
v13	#x[9]
o0	# + 
v13	#x[9]
n1
C19	#equilibrium[10]
o16	#-
o3	#/
o2	#*
n2
v14	#x[10]
o0	# + 
v14	#x[10]
n1
C20	#equilibrium[11]
o16	#-
o3	#/
o2	#*
n2
v15	#x[11]
o0	# + 
v15	#x[11]
n1
C21	#equilibrium[12]
o16	#-
o3	#/
o2	#*
n2
v16	#x[12]
o0	# + 
v16	#x[12]
n1
C22	#equilibrium[13]
o16	#-
o3	#/
o2	#*
n2
v17	#x[13]
o0	# + 
v17	#x[13]
n1
C23	#equilibrium[14]
o16	#-
o3	#/
o2	#*
n2
v18	#x[14]
o0	# + 
v18	#x[14]
n1
C24	#equilibrium[15]
o16	#-
o3	#/
o2	#*
n2
v19	#x[15]
o0	# + 
v19	#x[15]
n1
C25	#equilibrium[16]
o16	#-
o3	#/
o2	#*
n2
v20	#x[16]
o0	# + 
v20	#x[16]
n1
C26	#equilibrium[17]
o16	#-
o3	#/
o2	#*
n2
v21	#x[17]
o0	# + 
v21	#x[17]
n1
C27	#equilibrium[18]
o16	#-
o3	#/
o2	#*
n2
v22	#x[18]
o0	# + 
v22	#x[18]
n1
C28	#total_condenser
n0
C29	#reactor_is_stage_0
n0
C30	#tray_component_balances[1]
o1	# - 
o2	#*
v0	#V
v25	#y[1]
o2	#*
v0	#V
v24	#y[0]
C31	#tray_component_balances[2]
o1	# - 
o2	#*
v0	#V
v26	#y[2]
o2	#*
v0	#V
v25	#y[1]
C32	#tray_component_balances[3]
o1	# - 
o2	#*
v0	#V
v27	#y[3]
o2	#*
v0	#V
v26	#y[2]
C33	#tray_component_balances[4]
o1	# - 
o2	#*
v0	#V
v28	#y[4]
o2	#*
v0	#V
v27	#y[3]
C34	#tray_component_balances[5]
o1	# - 
o2	#*
v0	#V
v29	#y[5]
o2	#*
v0	#V
v28	#y[4]
C35	#tray_component_balances[6]
o1	# - 
o2	#*
v0	#V
v30	#y[6]
o2	#*
v0	#V
v29	#y[5]
C36	#tray_component_balances[7]
o1	# - 
o2	#*
v0	#V
v31	#y[7]
o2	#*
v0	#V
v30	#y[6]
C37	#tray_component_balances[8]
o1	# - 
o2	#*
v0	#V
v32	#y[8]
o2	#*
v0	#V
v31	#y[7]
C38	#tray_component_balances[9]
o1	# - 
o2	#*
v0	#V
v33	#y[9]
o2	#*
v0	#V
v32	#y[8]
C39	#tray_component_balances[10]
o1	# - 
o2	#*
v0	#V
v34	#y[10]
o2	#*
v0	#V
v33	#y[9]
C40	#tray_component_balances[11]
o1	# - 
o2	#*
v0	#V
v35	#y[11]
o2	#*
v0	#V
v34	#y[10]
C41	#tray_component_balances[12]
o1	# - 
o2	#*
v0	#V
v36	#y[12]
o2	#*
v0	#V
v35	#y[11]
C42	#tray_component_balances[13]
o1	# - 
o2	#*
v0	#V
v37	#y[13]
o2	#*
v0	#V
v36	#y[12]
C43	#tray_component_balances[14]
o1	# - 
o2	#*
v0	#V
v38	#y[14]
o2	#*
v0	#V
v37	#y[13]
C44	#tray_component_balances[15]
o1	# - 
o2	#*
v0	#V
v39	#y[15]
o2	#*
v0	#V
v38	#y[14]
C45	#tray_component_balances[16]
o1	# - 
o2	#*
v0	#V
v40	#y[16]
o2	#*
v0	#V
v39	#y[15]
C46	#tray_component_balances[17]
o1	# - 
o2	#*
v0	#V
v41	#y[17]
o2	#*
v0	#V
v40	#y[16]
C47	#tray_component_balances[18]
o1	# - 
o2	#*
v0	#V
v42	#y[18]
o2	#*
v0	#V
v41	#y[17]
d48	# initial dual guess
0 0
1 0
2 0
3 0
4 0
5 0
6 0
7 0
8 0
9 0
10 0
11 0
12 0
13 0
14 0
15 0
16 0
17 0
18 0
19 0
20 0
21 0
22 0
23 0
24 0
25 0
26 0
27 0
28 0
29 0
30 0
31 0
32 0
33 0
34 0
35 0
36 0
37 0
38 0
39 0
40 0
41 0
42 0
43 0
44 0
45 0
46 0
47 0
x48	# initial guess
0 277.7328698504927
1 0.5861813495489135
2 0.08608275842391994
3 140.7090972575802
4 51.32090207291207
5 0.5910844835079699
6 0.5973858016043722
7 0.6053688974822119
8 0.6153926349309299
9 0.6278383467788372
10 0.6430779398472152
11 0.6614241740409472
12 0.6830638745204883
13 0.7079818712215126
14 0.7358926703536963
15 0.766204290328097
16 0.7980380801761265
17 0.8303149586107575
18 0.8618947905486393
19 0.8917329376607532
20 0.9190101441134501
21 0.943204039420344
22 0.964094745761846
23 0.9817191842044446
24 0.7390817454019798
25 0.7429957235543256
26 0.7479543151340537
27 0.7541804235099641
28 0.7619109083891823
29 0.7713767746425927
30 0.7827722888372829
31 0.7962134948842607
32 0.8116909701041213
33 0.8290273839065356
34 0.8478550349677136
35 0.8676281611721752
36 0.8876765058343353
37 0.9072918895322336
38 0.9258254493558389
39 0.9427683156710176
40 0.9577960251448562
41 0.9707720036560338
42 0.9817191842235354
43 0.7390817459560045
44 105.22286985049286
45 32.35852262877177
46 64.70752086750426
47 137.00282597216855
r	#48 ranges (rhs's)
4 -172.51
4 0
4 0
4 -460
4 0
4 0
4 -38198.64
4 0
4 0
4 -10513
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
4 0
b	#48 bounds (on variables)
2 172.51
0 0 1
2 0
3
2 50
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
0 0 1
3
3
3
3
3
3
3
3
3
3
3
3
3
3
3
3
3
3
3
0 0 1
3
3
3
3
k47	#intermediate Jacobian column lengths
22
25
28
32
35
39
42
45
48
51
54
57
60
63
66
69
72
75
78
81
84
87
90
92
94
97
100
103
106
109
112
115
118
121
124
127
130
133
136
139
142
145
148
151
153
155
158
J0 2
0 -1
44 1
J1 2
3 0
45 1
J2 2
3 0
46 1
J3 2
5 0
47 1
J4 3
1 0
2 1
3 0
J5 4
0 0
2 1200
5 172.51
43 0
J6 5
0 -333.3333333333333
2 640000
3 0
44 140
47 172.51
J7 4
1 0
4 1
45 0
46 0
J8 4
1 0
4 0
43 0
46 0
J9 2
0 1
4 -210.26
J10 2
5 0
25 1
J11 2
6 0
26 1
J12 2
7 0
27 1
J13 2
8 0
28 1
J14 2
9 0
29 1
J15 2
10 0
30 1
J16 2
11 0
31 1
J17 2
12 0
32 1
J18 2
13 0
33 1
J19 2
14 0
34 1
J20 2
15 0
35 1
J21 2
16 0
36 1
J22 2
17 0
37 1
J23 2
18 0
38 1
J24 2
19 0
39 1
J25 2
20 0
40 1
J26 2
21 0
41 1
J27 2
22 0
42 1
J28 2
23 1
42 -1
J29 2
24 1
43 -1
J30 5
0 0
5 172.51
6 -172.51
24 0
25 0
J31 5
0 0
6 172.51
7 -172.51
25 0
26 0
J32 5
0 0
7 172.51
8 -172.51
26 0
27 0
J33 5
0 0
8 172.51
9 -172.51
27 0
28 0
J34 5
0 0
9 172.51
10 -172.51
28 0
29 0
J35 5
0 0
10 172.51
11 -172.51
29 0
30 0
J36 5
0 0
11 172.51
12 -172.51
30 0
31 0
J37 5
0 0
12 172.51
13 -172.51
31 0
32 0
J38 5
0 0
13 172.51
14 -172.51
32 0
33 0
J39 5
0 0
14 172.51
15 -172.51
33 0
34 0
J40 5
0 0
15 172.51
16 -172.51
34 0
35 0
J41 5
0 0
16 172.51
17 -172.51
35 0
36 0
J42 5
0 0
17 172.51
18 -172.51
36 0
37 0
J43 5
0 0
18 172.51
19 -172.51
37 0
38 0
J44 5
0 0
19 172.51
20 -172.51
38 0
39 0
J45 5
0 0
20 172.51
21 -172.51
39 0
40 0
J46 5
0 0
21 172.51
22 -172.51
40 0
41 0
J47 5
0 0
22 172.51
23 -172.51
41 0
42 0
