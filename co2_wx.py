#!/usr/bin/env python

# This is a hacked up version of code from: https://hackaday.io/project/5301/logs

import sys, fcntl, time, datetime

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

if __name__ == "__main__":
	# Key retrieved from /dev/random, guaranteed to be random ;)
	key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
    
	fp = open(sys.argv[1], "a+b",  0)
    
	HIDIOCSFEATURE_9 = 0xC0094806
	set_report = "\x00" + "".join(chr(e) for e in key)
	fcntl.ioctl(fp, HIDIOCSFEATURE_9, set_report)
    
	values = {}
    
	time0 = time1 = time.time()

	while True:
		data = list(ord(e) for e in fp.read(8))
		decrypted = decrypt(key, data)
		if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
			print hd(data), " => ", hd(decrypted),  "Checksum error"
		else:
			op = decrypted[0]
			val = decrypted[1] << 8 | decrypted[2]
            
		values[op] = val

		co2_val = 0
		co2_count = 0
		t_val = 0
		t_count = 0

		## From http://co2meters.com/Documentation/AppNotes/AN146-RAD-0401-serial-communication.pdf
		if 0x50 in values:
			co2_val += values[0x50]
			co2_count += 1
		if 0x42 in values:
			t_val += (values[0x42]/16.0-273.15)
			t_count += 1
		time1 = time.time()
		if((time1 - time0) > 5):
			ts =  datetime.datetime.fromtimestamp(time1).strftime("%Y%m%d%H%M%S")
			print "%s\tT: %2.2f\tCO2: %4i" % (ts, t_val / t_count, co2_val / co2_count)
			co2_val = 0
			co2_count = 0
			t_val = 0
			t_count = 0
			time0 = time1 = time.time()	
