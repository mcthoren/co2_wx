set term pngcairo size 2000, 512 font ",10"
set title "Average Daily CO_2 Levels"
set y2tics
set mytics
set key outside below
set xdata time
set timefmt "%Y%m%d"
set xlabel "Time (UTC)" offset 0.0, -1.6
set format x "%F"
set grid
set ylabel "CO_2 (ppm)"
set y2label "CO_2 (ppm)"
set xtics auto rotate by 30 offset -6.8, -2.2
set mxtics 
set xrange [:] noextend
set grid mxtics

dat_f="~/co2_wx/data/co2.day.avg"
dat_f_30="~/co2_wx/data/co2.day.avg.30"

set style fill solid 0.50 noborder
set output "~/co2_wx/plots/co2_day_avgs.png"
plot dat_f using 1:5 t 'CO_2 (ppm)' with boxes linecolor rgb "#0000ff"

set title "Average Daily CO_2 Levels for the last 30 Days"
set style fill solid 0.50 noborder
set output "~/co2_wx/plots/co2_day_avgs.30.png"
plot dat_f_30 using 1:5 t 'CO_2 (ppm)' with boxes linecolor rgb "#0000ff"
