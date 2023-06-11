set title "CO_{2} from mh-z14a"
set xtics 7200 rotate by 30 offset -5.7, -2.2
set ytics
set y2tics
set link y2
set mytics
set key outside below
set xlabel "Time (UTC)" offset 0.0, -1.6
set xdata time;
set format x "%F\n%TZ"
set timefmt "%Y-%m-%dT%H:%M:%S%Z"
set grid xtics
set grid y2tics
set term pngcairo size 2000, 512 font ",10"

set format y "%.1f"
set format y2 "%.1f"

dat_f="/import/home/ghz/repos/co2_wx/data/co2.dat.48_hours"

set ylabel "CO_{2} (ppm)"
set y2label "CO_{2} (ppm)"
set output "~/repos/co2_wx/plots/room_co2.png"
plot dat_f using 1:3 title 'CO_{2}' with lines lw 2 linecolor rgb "#00dddd"
