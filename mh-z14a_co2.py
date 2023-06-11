#!/usr/bin/python3
# -*- coding: utf-8 -*-

# the plan here is to collect and write out data from
# what i think is a Winsen MH-Z14A NDIR CO₂ Module.

# datasheet:
# https://www.winsen-sensor.com/d/files/MH-Z14A.pdf

# website:
# https://www.winsen-sensor.com/sensors/co2-sensor/mh-z14a.html

import serial, struct, sys, time

sys.path.append('/import/home/ghz/repos/wxlib')
import wxlib as wx

wx_dir = "/import/home/ghz/co2_wx"

port='/dev/ttyUSB0'
read_co2_c = [0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]

# 0 - 2000 ppm
# detect_range_c = [0xff, 0x01, 0x99, 0x00, 0x00, 0x00, 0x07, 0xd0, 0x8f]

# 0 - 5000 ppm
detect_range_c = [0xff, 0x01, 0x99, 0x00, 0x00, 0x00, 0x13, 0x88, 0xcb]

# 0 - 10000 ppm XXX not yet tested!!
# detect_range_c = [0xff, 0x01, 0x99, 0x00, 0x00, 0x00, 0x27, 0x10, 0x2f]

# 20min @ 400ppm
zero_point_cal_c = [0xff, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78]

debug = 1
def init_port(p_dev):
	p_dev.flushInput()
	p_dev.flushOutput()
	p_dev.write(bytearray(detect_range_c))

if __name__ == '__main__':
	dat_fname = 'co2.dat'

	port_dev = serial.Serial(port, 9600, timeout = 1)
	init_port(port_dev)
	
	itr = 0
	co2_ppm = 0.0
	while True:
		port_dev.write(bytearray(read_co2_c))
		read_bytes = port_dev.read(9)
		if len(read_bytes) == 9:
			# big endian: start byte, cmd, high byte, low byte, -, -, -, -, checksum
			vals = struct.unpack(">cchccccc", read_bytes)
			co2_ppm += vals[2]
			itr += 1
			if debug:
				tsd = time.strftime("%FT%TZ", time.gmtime())
				print(tsd, "\t", "CO₂:", vals[2], "ppm")

			if read_bytes[8] != 0xff & (~ sum(read_bytes[1:8]) + 1):
				print("checksum failed!")
				print("check sum: ", read_bytes[8])
				print("calc sum: ", 0xff & (~ sum(read_bytes[1:8]) + 1), "\n")
				time.sleep(1)
				init_port(port_dev)
				continue

		if itr >= 58:
			ts = time.strftime("%FT%TZ", time.gmtime())
			dat_s = "{0:s}\tCO₂: {1:0.1f} ppm\n".format(ts, co2_ppm / itr, "utf-8")
			wx.write_out_dat_stamp_iso(ts, dat_fname, dat_s, wx_dir)
			itr = 0
			co2_ppm = 0.0

		time.sleep(1)

