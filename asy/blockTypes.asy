struct cell {
  int i;
  int j;

  void operator init(int i, int j) {
    this.i = i;
    this.j = j;
  }
}

struct rectangle {

  pair up_right;
  pair down_left;

  void operator init(pair up_right, pair down_left) {
    this.up_right  = up_right;
    this.down_left = down_left;
  }
};

struct block_edges {

  string row_first;
  string row_last;
  string col_first;
  string col_last;

  bool to_plot() {

    return (length(row_first)>0)&&
           (length(row_last) >0)&&
           (length(col_first)>0)&&
           (length(col_last) >0);
  } 

  void operator init(string row_first, string row_last, string col_first, string col_last) {
    this.row_first = row_first;
    this.row_last  = row_last;
    this.col_first = col_first;
    this.col_last  = col_last;
  }

};

struct block {
 
  string row_up_right;
  string col_up_right;
  int x_size;
  int y_size;
 
  void operator init(string row_up_right, string col_up_right, int x_size, int y_size=x_size) {
     this.row_up_right = row_up_right;
     this.col_up_right = col_up_right;
     this.x_size = x_size;
     this.y_size = y_size;
  }
};
