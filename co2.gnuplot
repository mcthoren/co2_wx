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

HOME=system('echo "${HOME}"')
dat_f=HOME."/repos/co2_wx/data/co2.dat.2-3_day"

# plot nothing to set range, so y2 can use it later w.o. throwing an error.
# this isn't necessary in gnuplot v5.2p6, but now in 5.4p1 it is? you would think
# "set y2tics mirror" or similar would sort it, but i haven't managed to make anything work yet.
set output "| cat > /dev/null"
plot dat_f using 1:6

set y2range [GPVAL_Y_MIN:GPVAL_Y_MAX]
set y2tics
set ylabel "CO_{2} (ppm)"
set y2label "CO_{2} (ppm)"
set output HOME."/repos/co2_wx/plots/room_co2.png"
plot dat_f using 1:6 title 'CO_{2}' with lines lw 2 linecolor rgb "#00dd00"

unset y2tics
set output "| cat > /dev/null"
plot dat_f using 1:3

set y2range [GPVAL_Y_MIN:GPVAL_Y_MAX]
set y2tics
set ylabel "Temp (°C)"
set y2label "Temp (°C)"
set output HOME."/repos/co2_wx/plots/room_temp.png"
plot dat_f using 1:3 title 'Temp' with lines lw 2 linecolor rgb "#0000dd"
