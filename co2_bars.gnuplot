set y2tics
set key outside below
set grid
set ylabel "CO₂ (ppm)"
set y2label "CO₂ (ppm)"
set term pngcairo size 2000, 512 font ",10"
set xtics auto
set mxtics 
set grid mxtics

dat_f='/home/ghz/co2_wx/data/co2.day.avg'

set title "Average Daily CO₂ Levels"
set output '/home/ghz/co2_wx/data/plots/co2_day_avgs.png'
plot dat_f using 1:3 t 'CO₂ (ppm)' with boxes linecolor rgb "#ff0000"
