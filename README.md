Structure-driven optimization methods for modular technical systems
===================================================================

- <a name="structure-driven"></a> 
The term **structure-driven** refers to the following idea. First, we partition 
the large, sparse nonlinear model of a technical system into smaller 
subproblems. Then, a suitable ordering of these smaller problems is determined 
so that the solution to the original problem can be reconstructed from the 
solutions of the smaller ones. The decomposition just sketched resembles the
[tree decomposition](http://en.wikipedia.org/wiki/Tree_decomposition#Dynamic_programming), 
which is very popular in discrete optimization and constraint satisfaction; this 
project deals with *continuous* problems. Evidence shows that appropriate 
decomposition can speed up the computations by several orders of magnitude.
- [Nonlinear programming](http://en.wikipedia.org/wiki/Nonlinear_programming) 
is meant by **optimization**.
- The image below shows an example of a **modular technical system**
(a heating system, the image has been taken from the 
[Modelica website](https://www.modelica.org/news_items/release_of_modelica_fluid_1_0)).
Component-based modeling is well suited for modular technical systems; 
[Simulink](http://en.wikipedia.org/wiki/Simulink) and 
[Dymola](http://en.wikipedia.org/wiki/Dymola) are examples of component-based 
modeling tools. The modules (components) of the technical systems help in 
decomposing the large model into smaller problems.
<p align="center">
  <img src ="pics/HeatingSystem.png?raw=true" alt="modular technical system"/>
</p>

**THIS PROJECT IS A WORK IN PROGRESS.**

Input
-----
Currently, the models are written in [AMPL](http://en.wikipedia.org/wiki/AMPL),
and after some black magic, the expressions are built-up in memory as a 
direct acyclic graph (DAG), using
[NetworkX DiGraph](http://networkx.github.io/documentation/latest/reference/classes.digraph.html).
It is somewhat similar to the 
[expression trees](http://docs.sympy.org/latest/tutorial/manipulation.html) in 
SymPy. Only nonlinear systems of equations are considered at the moment 
(steady-state modeling).

For example, the following AMPL code
```
var x; var y; var z;
equation: exp(3*x+2*y)+4*z = 1;
```
yields the directed acyclic graph below.
<p align="center">
  <img src="pics/example.png?raw=true" alt="expression tree"/>
</p>
In the future, I would like to use either Python or 
[JuMP](https://github.com/JuliaOpt/JuMP.jl) for building the models. 
In any case, I will keep the AMPL interface too. 
[Modelica](http://en.wikipedia.org/wiki/Modelica) is definitely on the agenda, 
accessed through the 
[functional mock-up interface](http://en.wikipedia.org/wiki/Functional_Mock-up_Interface).
This project is not aiming at creating yet another modeling environment: The 
goal is to plug the tools of this project into well-established modeling 
systems.

Natural block structure
-----------------------
The modules of the technical systems partition the 
[Jacobian](http://en.wikipedia.org/wiki/Jacobian_matrix_and_determinant) 
into blocks in a fairly natural way. This natural block structure plays an
important role in [structure-driven algorithms](README.md#structure-driven):
Computing the optimal partitioning and ordering of the smaller subproblems is 
NP-hard in the general case; one must resort to heuristics in practice. 
Independent results show that the heuristic which exploits the natural block 
structure often yields good quality partitioning and ordering. 

The current way to pass the natural blocks is rather hackish: Suffixes are 
used, see *Defining and using suffixes* on page 302 in the 
[AMPL book](http://ampl.github.io/ampl-book.pdf). In the future, component-based
modeling tools will hopefully allow programmatic access to the natural block 
structure.

Minimum degree ordering
-----------------------
A basic minimum degree ordering has been implemented. The blue lines show the 
natural block structure.

![ordering](pics/ordering.png?raw=true)

My primary interest is chemical process modeling. The Jacobian of these models 
are very sparse but *highly* unsymmetric, numerically indefinite, not diagonally 
dominant and possibly ill-conditioned. There are many packages for the symmetric 
and slightly unsymmetric case. (In the slightly unsymmetric case, it is 
acceptable to introduce artificial fill-in to make the sparsity pattern 
symmetric and then use a sparse matrix ordering algorithm, developed for the 
symmetric case.) I have only found 
[MC33 from the Harwell Subroutine Library](http://www.hsl.rl.ac.uk/catalogue/mc33.html)
that is applicable in the highly unsymmetric case. Since MC33 is based on a 
heuristic, it unfortunately fails on those chemical process models that are of 
interest to me.

Graph coloring
--------------
Efficient 
[automatic differentiation](http://en.wikipedia.org/wiki/Automatic_differentiation) 
(AD) requires a smart selection of seed vectors, which can be computed with 
[graph coloring](http://en.wikipedia.org/wiki/Graph_coloring). Even though the 
problem is NP-complete in general, the minimum degree ordering enables an 
efficient 
[greedy coloring heuristic](http://en.wikipedia.org/wiki/Greedy_coloring).

![coloring](pics/coloring.png?raw=true)
