
In the ~/.profile

PATH="$PATH:$HOME/ampl-bin:$HOME/bin"

This is the way to get all options:

$ ampl
ampl: option OPTIONS_INOUT 'amplopts.txt';
ampl: quit;

Then add the following line to ~/.profile

export OPTIONS_IN=$HOME/ampl/amplopts.txt




