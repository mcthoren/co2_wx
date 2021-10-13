#!/usr/local/bin/python3

# the plan here is to collect and write out data from
# what i think is a Winsen MH-Z14A NDIR CO₂ Module.

# datasheet:
# https://www.winsen-sensor.com/d/files/MH-Z14A.pdf

# website:
# https://www.winsen-sensor.com/sensors/co2-sensor/mh-z14a.html

import serial, struct, sys, time

sys.path.append('/home/ghz/repos/wxlib')
import wxlib as wx

wx_dir = "/tmp/co2"

port='/dev/ttyU0'
read_co2_c = [0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]

# 0 - 2000 ppm
detect_range_c = [0xff, 0x01, 0x99, 0x00, 0x00, 0x00, 0x07, 0xd0, 0x8f]

# 20min @ 400ppm
zero_point_cal_c = [0xff, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78]

if __name__ == '__main__':
	dat_fname = 'co2.dat'

	port_dev = serial.Serial(port, 9600, timeout = 1)
	port_dev.flushInput()
	port_dev.flushOutput()
	port_dev.write(bytearray(detect_range_c))
	
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

			if read_bytes[8] != 0xff & (~ sum(read_bytes[1:8]) + 1):
				print("checksum failed!")
				print("check sum: ", read_bytes[8])
				print("calc sum: ", 0xff & (~ sum(read_bytes[1:8]) + 1), "\n")
				time.sleep(1)
				continue

		if itr >= 58:
			ts = time.strftime("%FT%TZ", time.gmtime())
			dat_s = "{0:s}\tCO₂: {1:0.1f} ppm\n".format(ts, co2_ppm / itr, "utf-8")
			wx.write_out_dat_stamp_iso(ts, dat_fname, dat_s, wx_dir)
			itr = 0
			co2_ppm = 0.0

		time.sleep(1)

