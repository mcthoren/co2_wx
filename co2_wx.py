#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this code indented with actual 0x09 tabs

# This is a hacked up version of code from: https://hackaday.io/project/5301/logs

import sys, fcntl, time, datetime, os, fileinput
import numpy as np
import matplotlib.dates as mdates

base_dir = "/import/home/ghz"
wx_dir = base_dir+'/co2_wx'
wxlib_dir = base_dir+'/wxlib'
plot_d = wx_dir+'/plots/'
wx_user = "wx4"

sys.path.append(wxlib_dir)
import wxlib as wx

def plot(ts, n_plate):
	npoints = 2200 # ~48h

	d_date = ["0000", "0000", "0000", "0000"]
	d_year = ["0000", "0000", "0000", "0000"]

	td = datetime.datetime.strptime(ts, "%Y%m%d%H%M%S")

	for i in range(0, 4):
		d_date[i] = (td - datetime.timedelta(i)).strftime("%Y%m%d")
		d_year[i] = (td - datetime.timedelta(i)).strftime("%Y")

	dat_f0 = wx_dir+'/data/'+d_year[0]+'/'+n_plate+'.'+d_date[0]
	dat_f1 = wx_dir+'/data/'+d_year[1]+'/'+n_plate+'.'+d_date[1]
	dat_f2 = wx_dir+'/data/'+d_year[2]+'/'+n_plate+'.'+d_date[2]
	dat_f3 = wx_dir+'/data/'+d_year[3]+'/'+n_plate+'.'+d_date[3]

	co2_dat  = fileinput.input([dat_f3, dat_f2, dat_f1, dat_f0])
	date, temp, co2 = np.loadtxt(co2_dat, usecols=(0, 2, 5), unpack=True, converters={ 0: mdates.strpdate2num('%Y%m%d%H%M%S')})

	if date.size < npoints:
		npoints = date.size - 1

	f_pts  = date.size - npoints
	t_pts  = date.size

	wx.graph(date[f_pts : t_pts], temp[f_pts : t_pts], "b-", "Temperature", u"Temp (°C)", plot_d+'room_temp.png')
	wx.graph(date[f_pts : t_pts], co2[f_pts : t_pts], "g-", u"CO₂ Levels", u"CO₂ (ppm)", plot_d+'room_co2.png')

def decrypt(key,  data):
	cstate = [0x48,  0x74,  0x65,  0x6D,  0x70,  0x39,  0x39,  0x65]
	shuffle = [2, 4, 0, 7, 1, 6, 5, 3]
    
	phase1 = [0] * 8
	for i, o in enumerate(shuffle):
		phase1[o] = data[i]
    
	phase2 = [0] * 8
	for i in range(8):
		phase2[i] = phase1[i] ^ key[i]
    
	phase3 = [0] * 8
	for i in range(8):
		phase3[i] = ( (phase2[i] >> 3) | (phase2[ (i-1+8)%8 ] << 5) ) & 0xff
    
	ctmp = [0] * 8
	for i in range(8):
		ctmp[i] = ( (cstate[i] >> 4) | (cstate[i]<<4) ) & 0xff
    
	out = [0] * 8
	for i in range(8):
		out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff
    
	return out

def hd(d):
	return " ".join("%02X" % e for e in d)

def gen_index(co2, temp):
	plate = wx_dir+"/co2_wx_index.html.template"
	plate_fd = open(plate, 'r')
	plate_dat = plate_fd.read()
	plate_fd.close()

	ts = datetime.datetime.fromtimestamp(time.time()).strftime("%FT%TZ")

	plate_dat = plate_dat.replace("CO2", str(co2))
	plate_dat = plate_dat.replace("ROOMTEMP", str("%.2f" % temp))
	plate_dat = plate_dat.replace("DATE", ts)

	wx.write_out(wx_dir+'/plots/co2_wx.html', plate_dat, 'w')

if __name__ == "__main__":
	# Key retrieved from /dev/random, guaranteed to be random ;)
	key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
    
	fp = open(sys.argv[1], "a+b",  0)

	dat_fname = 'co2.dat'
	wx.proof_dir(plot_d)
    
	HIDIOCSFEATURE_9 = 0xC0094806
	set_report = "\x00" + "".join(chr(e) for e in key)
	fcntl.ioctl(fp, HIDIOCSFEATURE_9, set_report)
    
	values = {}
    
	time0 = time1 = time.time()

	while True:
		try:
			data = list(ord(e) for e in fp.read(8))
		except IOError:
			# sometimes the usb brainfreezes. give it a tick, and try again
			print "omg ioerror 0"
			time.sleep(1)
			continue

		decrypted = decrypt(key, data)
		if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
			print hd(data), " => ", hd(decrypted),  "Checksum error"
		else:
			op = decrypted[0]
			val = decrypted[1] << 8 | decrypted[2]
			values[op] = val

		co2_val = co2_count = t_val = t_count = 0

		## From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
		if 0x50 in values:
			co2_val += values[0x50]
			co2_count += 1
		if 0x42 in values:
			t_val += (values[0x42]/16.0-273.15)
			t_count += 1
		time1 = time.time()
		if((time1 - time0) > 60):
			ts =  datetime.datetime.fromtimestamp(time1).strftime("%Y%m%d%H%M%S")
			temp = t_val / t_count
			co2 = co2_val / co2_count
			dat_string = "%s\tT: %2.2f C\tCO2: %4i ppm\n" % (ts, temp, co2)
			wx.write_out_dat_stamp(ts, dat_fname, dat_string, wx_dir)
			plot(ts, dat_fname)
			gen_index(co2, temp)
			os.system('/usr/bin/rsync -ur --timeout=60 '+wx_dir+'/* '+wx_user+'@darkdata.org:/'+wx_user+'/')
			co2_val = co2_count = t_val = t_count = 0
			time0 = time1 = time.time()	
