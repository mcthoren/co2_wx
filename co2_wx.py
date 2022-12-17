#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is a hacked up version of code from: https://hackaday.io/project/5301/logs

import sys, fcntl, time, datetime, os, fileinput, argparse
import numpy as np
import matplotlib.dates as mdates

def plot(ts, n_plate):
	npoints = 2200 # ~48h

	dat_f = ["0000", "0000", "0000", "0000"]

	td = datetime.datetime.strptime(ts, "%Y%m%d%H%M%S")

	for i in range (0, 4):
		d_date = (td - datetime.timedelta(i)).strftime("%Y%m%d")
		d_year = (td - datetime.timedelta(i)).strftime("%Y")
		dat_f[3 - i] = wx_dir+'/data/'+d_year+'/'+n_plate+'.'+d_date
		wx.proof_dat_f(dat_f[3 - i])

	co2_dat = fileinput.input(dat_f)
	date, temp, co2 = np.loadtxt(co2_dat, usecols = (0, 2, 5), unpack = True, encoding = u'utf8', converters={ 0: mdates.strpdate2num('%Y%m%d%H%M%S')})

	if date.size < 4:
		return 0; # not enough points yet. wait for more

	if date.size < npoints:
		npoints = date.size - 1

	f_pts  = date.size - npoints
	t_pts  = date.size

	wx.graph(date[f_pts : t_pts], temp[f_pts : t_pts], "b-", u"Temperature", u"Temp (°C)", plot_d+'room_temp.png')
	wx.graph(date[f_pts : t_pts], co2[f_pts : t_pts], "g-", u"CO₂ Levels", u"CO₂ (ppm)", plot_d+'room_co2.png')

def decrypt(data):
	cstate = [0x48,  0x74,  0x65,  0x6D,  0x70,  0x39,  0x39,  0x65]
	shuffle = [2, 4, 0, 7, 1, 6, 5, 3]
    
	phase1 = [0] * 8
	for i, o in enumerate(shuffle):
		phase1[o] = data[i]
    
	phase3 = [0] * 8
	for i in range(8):
		phase3[i] = ( (phase1[i] >> 3) | (phase1[ (i-1+8)%8 ] << 5) ) & 0xff
    
	ctmp = [0] * 8
	for i in range(8):
		ctmp[i] = ( (cstate[i] >> 4) | (cstate[i]<<4) ) & 0xff
    
	out = [0] * 8
	for i in range(8):
		out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff
    
	return out

def hd(d):
	return " ".join("0x%02x" % e for e in d)

def gen_index(co2, temp, title):
	plate = wx_dir+"/co2_wx_index.html.template"
	plate_fd = open(plate, 'r')
	plate_dat = plate_fd.read()
	plate_fd.close()

	ts = time.strftime("%FT%TZ", time.gmtime())

	plate_dat = plate_dat.replace("CO2", str("%.0f" % co2))
	plate_dat = plate_dat.replace("ROOMTEMP", str("%.2f" % temp))
	plate_dat = plate_dat.replace("TITLE", title)
	plate_dat = plate_dat.replace("DATE", ts)

	wx.write_out(wx_dir+'/plots/co2_wx.html', plate_dat, 'w')

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description=u'Read CO₂ data, and then upload it somewhere.')

	parser.add_argument('--debug', dest = 'debug', action = 'store_true', help = u'dump pre and post decrypt data')
	group = parser.add_mutually_exclusive_group()
	group.add_argument('--indoor', dest = 'probe_in', action = 'store_true', help = u'setup everything for the indoor probe')
	group.add_argument('--outdoor', dest = 'probe_out', action = 'store_true', help = u'setup eveyrthing for the outdoor probe')

	args = parser.parse_args()

	if (args.probe_in):
		# spiffy
		co2_dev = "/dev/co2_sensor0"
		base_dir = "/import/home/ghz"
		wx_user = "wx4"
		title = "CO₂ levels from a room in Augsburg, Germany"

	if (args.probe_out):
		# elf
		co2_dev = "/dev/co2_sensor0"
		base_dir = "/home/ghz"
		wx_user = "wx2"
		title = "CO₂ levels from a balcony in Berlin"

	if ((args.probe_in | args.probe_out) == 0):
		print("please use either the --indoor or --outdoor option to select a probe")
		exit()

	if (args.probe_in & args.probe_out):
		print("this shouldn't happen. please select just one probe.")
		exit()

	wx_dir = base_dir+'/co2_wx'
	plot_d = wx_dir+'/plots/'

	wxlib_dir = base_dir+'/wxlib'
	sys.path.append(wxlib_dir)
	import wxlib as wx

	fp = open(co2_dev, "a+b",  0)

	dat_fname = 'co2.dat'
	wx.proof_dir(plot_d)
    
	# just send the stupid thing a bunch of zeros and skip any complications with a key
	HIDIOCSFEATURE_9 = 0xC0094806
	fcntl.ioctl(fp, HIDIOCSFEATURE_9, "\x00" * 9)
    
	values = {}
    
	time0 = time1 = time.time()
	co2_val = co2_count = t_val = t_count = 0

	while True:
		try:
			data = fp.read(8)
		except IOError:
			# sometimes the usb brainfreezes. give it a tick, and try again
			print("omg ioerror 0")
			time.sleep(1)
			continue

		decrypted = decrypt(data)
		if args.debug:
			print(hd(data), " => ", hd(decrypted))
		if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
			print(hd(data), " => ", hd(decrypted),  "Checksum error")
		else:
			op = decrypted[0]
			val = decrypted[1] << 8 | decrypted[2]
			values[op] = val

		## From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
		if 0x50 in values:
			co2_val += values[0x50]
			co2_count += 1
		if 0x42 in values:
			t_val += (values[0x42]/16.0-273.15)
			t_count += 1
		time1 = time.time()
		if((time1 - time0) > 60):
			ts = time.strftime("%Y%m%d%H%M%S", time.gmtime(float(time1)))
			temp = t_val / t_count
			co2 = co2_val / co2_count
			dat_string = "%s\tT: %2.2f C\tCO2: %4i ppm\n" % (ts, temp, co2)
			wx.write_out_dat_stamp(ts, dat_fname, dat_string, wx_dir)
			plot(ts, dat_fname)
			gen_index(co2, temp, title)
			os.system('/usr/bin/rsync -ur --timeout=60 '+wx_dir+'/* '+wx_user+'@darkdata.org:/'+wx_user+'/')
			co2_val = co2_count = t_val = t_count = 0
			time0 = time1 = time.time()	
