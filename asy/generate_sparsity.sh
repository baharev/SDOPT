asy -f pdf -u draw_empty=false -u above_diagonal=black -u psize=1500 -u write_names=false plot.asy

nohup okular plot.pdf >/dev/null 2>&1 &
