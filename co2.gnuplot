set title "CO₂"
set xtics 7200 rotate by 30 offset -5.7, -2.2
set ytics
set mytics
set y2tics
set key outside below
set xlabel "Time (UTC)" offset 0.0, -1.6
set xdata time;
set format x "%F\n%TZ"
set timefmt "%Y-%m-%dT%H:%M:%S"
set grid xtics
set grid y2tics
set term pngcairo size 2000, 512 font ",10"

set format y "%.1f"
set format y2 "%.1f"

dat_f="/tmp/co2/data/co2.dat.2-3_day"

set ylabel "CO₂ (ppm)"
set y2label "CO₂ (ppm)"
set output "/tmp/mh-co2.png"
plot dat_f using 1:3 title 'CO₂' with lines lw 2 linecolor rgb "#0000dd"
