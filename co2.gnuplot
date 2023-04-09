set title "CO_{2}"
set xtics 7200 rotate by 30 offset -5.7, -2.2
set ytics
set mytics
set key outside below
set xlabel "Time (UTC)" offset 0.0, -1.6
set xdata time;
set format x "%F\n%TZ"
set timefmt "%Y%m%d%H%M%S"
set grid xtics
set grid y2tics
set term pngcairo size 2000, 512 font ",10"

set format y "%.1f"
# set format y2 "%.1f"

dat_f="/import/home/ghz/repos/co2_wx/data/co2.dat.2-3_day"

set ylabel "CO_{2} (ppm)"
set y2label "CO_{2} (ppm)"
set output "/import/home/ghz/repos/co2_wx/plots/room_co2.png"
plot dat_f using 1:6 title 'CO_{2}' with lines lw 2 linecolor rgb "#00dd00"

set ylabel "Temp (°C)"
set y2label "Temp (°C)"
set output "/import/home/ghz/repos/co2_wx/plots/room_temp.png"
plot dat_f using 1:3 title 'Temp' with lines lw 2 linecolor rgb "#0000dd"
