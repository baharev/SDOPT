import filename;
import pattern;
import names;
import blockTypes;
import generatedBlocks;
import blocks;

//---------------------
int psize = 5000;
bool draw_empty = true;
pen above_diagonal = red;
bool write_names = true;
// pen fat appears 3 times, 2 of them are different
//---------------------
usersetting();

size(psize, Aspect);

file frow = input(file_name+((generated_blocks.length==0)?".prow":".pbrow"));

string[] row_ampl_names = frow;

file fcol = input(file_name+((generated_blocks.length==0)?".pcol":".pbcol"));

string[] col_ampl_names = fcol;

real SCALE = 10.0;

if (write_names) {

for (int i=0; i<row_names.length; ++i) {

    string name = row_names[i];

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

rectangle cell_to_rectangle(int i, int j, int x_size=1, int y_size=x_size) {

    real a = j*SCALE;

    real b = a + (SCALE*x_size);

    real c = (-i)*SCALE;

    real d = c - (SCALE*y_size);

    return rectangle((a,c),(b,d));
}

path rectangle_to_path(rectangle r) {

    return r.up_right--(r.down_left.x, r.up_right.y)--(r.down_left)--(r.up_right.x, r.down_left.y)--cycle;
}

path cell_to_path(cell c, int x_size=1, int y_size=x_size) {

    return rectangle_to_path( cell_to_rectangle(c.i,c.j,x_size, y_size) );
}

for (int i=0; i<n_con; ++i) {
  for (int j=0; j<n_var; ++j) {

    path p = cell_to_path(cell(i,j));

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

int find(string s, string[] arr) {

  for (int i=0; i<arr.length; ++i) {
    if (s==arr[i]) {
      return i;
    }
  }
  abort("name "+s+" not found");
  return -1;
}

cell find(block b) {

  int row = find(b.row_up_right, row_ampl_names);
  int col = find(b.col_up_right, col_ampl_names);

  return cell(row,col);
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

  rectangle rec = cell_to_rectangle(r1, c1, x_size, y_size);

  return rectangle_to_path(rec);
}

void draw_blocks(block_edges[] edges, bool check_squareness=false) {

  path[] blks;

  for (block_edges b : edges) {

    if (b.to_plot()) {

      blks.append(block_edges_to_path(b, check_squareness));
    }
  }

  pen fat = black+3;

  for (path p : blks) {

    draw(p, fat);
  }
}

void draw_nested_blocks() {

  path[] blocks;

  for (block b : nested_blocks) {

    blocks.append(cell_to_path(find(b), b.x_size, b.y_size));

  }

  pen fat = black+linetype(new real[] {4,4})+3;

  for (path p : blocks) {

    draw(p, fat);
  }
}

draw_nested_blocks();

draw_blocks(generated_blocks, true);

draw_blocks(blocks);

if (!draw_empty) {
  pen fat = black+3;
  rectangle bbox = cell_to_rectangle(0, 0, col_names.length, row_names.length);
  draw(rectangle_to_path(bbox), fat);
}

