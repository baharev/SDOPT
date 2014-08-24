string file_name;
int psize = 5000;
bool draw_empty = true;
pen above_diagonal = red;
bool write_names = true;
pen fat = black + 3;
real SCALE = 10.0;
//------------
usersetting();
assert(length(file_name), "No file name given!");
size(psize, Aspect);

struct ipair {
    int i; int j;
    void operator init(int i, int j) { this.i = i; this.j = j; }
}

file frow = input(file_name+".row");
string[] row_ampl_names = frow;
int n_con = row_ampl_names.length;
file fcol = input(file_name+".col");
string[] col_ampl_names = fcol;
int n_var = col_ampl_names.length;
file frperm = input(file_name+".rperm");
int[] rperm = frperm;
file fcperm = input(file_name+".cperm");
int[] cperm = fcperm;
file frslc  = input(file_name+".rslc");
ipair[] rslc= frslc;
file fcslc  = input(file_name+".cslc");
ipair[] cslc= fcslc;

// TODO Can I group the name writing stuffs?
if (write_names) {
    for (int i=0; i<row_names.length; ++i) {
        string name = row_names[i]; // TODO Print filtered, permuted names
        real y = -(i+0.5)*SCALE;
        label(name, (0,           y), W);
        label(name, (n_var*SCALE, y), E);
    }
    for (int i=0; i<col_names.length; ++i) {
        string name = col_names[i];
        real x = (i+0.5)*SCALE;
        label(name, (x, 0), N);
        label(name, (x, -n_con*SCALE), S);
    }
}

path cell_to_path(int i, int j, int x_size=1, int y_size=x_size) {
    real a = j*SCALE;
    real b = a + (SCALE*x_size);
    real c = (-i)*SCALE;
    real d = c - (SCALE*y_size);
    return (a,c)--(b,c)--(b,d)--(a, d)--cycle;
}

// TODO Draw gray lines in the background first but never draw empty cells
//      Use a sparse matrix here, we are iterating it row-wise apparently
for (int i=0; i<n_con; ++i) {
    for (int j=0; j<n_var; ++j) {
        path p = cell_to_path(i, j);
        pen color = (j>i && A[i][j]!=0) ? above_diagonal : black;
        pen border = gray(0.8);
        if (A[i][j]!=0)
            filldraw(p, color, border);
        else if (draw_empty)
            draw(p, border);
    }
}

if (write_names) {
    label(file_name+" (var: "+(string) n_var+", con: "+(string) n_con+")",(SCALE*n_var/2.0, 1.5*SCALE));
}

path block_edges_to_path(block_edges e, bool check_squareness) {
    int r1 = find(e.row_first, row_ampl_names);
    int r2 = find(e.row_last,  row_ampl_names);
    int c1 = find(e.col_first, col_ampl_names);
    int c2 = find(e.col_last,  col_ampl_names);
    int x_size = c2-c1+1;
    int y_size = r2-r1+1;
    if (check_squareness && (x_size!=y_size)) {
        write( "WARNING: non-square block "+e.row_first+"("+((string)y_size)+"), "+e.col_first+"("+((string)x_size)+")");
    }
    return cell_to_path(r1, c1, x_size, y_size);
}

void draw_blocks(block_edges[] edges, bool check_squareness=false) {
    path[] blks;
    for (block_edges b : edges) {
        if (b.to_plot()) {
            blks.append(block_edges_to_path(b, check_squareness));
        }
    }
    for (path p : blks) {
        draw(p, fat);
    }
}

draw_blocks(generated_blocks, true);

if (!draw_empty) {
    path bounding_box = cell_to_path(0, 0, col_names.length, row_names.length);
    draw(bounding_box, fat);
}
