#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Parse Foxwell Tech cbf file into csv
Version 0.1 for python 2.7
Mike Ingle <inglem@pobox.com>
This code is in the public domain.

Foxwell Tech https://www.foxwelltech.com/ is a manufacturer of automotive
diagnostic devices. These devices can read OBD2 data as well as
manufacturer-specific data from the engine, transmission, body electrical and
other controllers in a vehicle. This code was tested on a NT520 Pro with the
OBD2 and Honda software.

The unit has a Save Data mode which continously records parameters from a
subsystem and writes to a proprietary file format with the extension CBF.
There is also a Playback mode on the device, which is supposed to display this
data. The Playback mode, as of this writing, is only partially functional for
OBD2 and not at all functional for the Honda module.

This program extracts the data from a Foxwell CBF file and converts it to CSV
which can be opened with a spreadsheet. The code was written from inspection
of the files, so it may not work for other modules or software versions. If
you have a CBF this program won't parse, please send it to me and I will
modify the parser.

The Foxwell unit has a USB port and a Micro SD card slot. The USB port does
not give access to the file system. To obtain the CBF file, after running a
capture, you must remove the card, plug it into an adapter, and connect it to
a PC. The CBF files for OBD2 are located at \Scan\OBDII\savefile and are
numbered consecutively.  The CBF files for Honda are at \Scan\Honda\savefile
so I assume other car brands will be in similar locations.

CBF file format:

This is a tabular format analogous to a CSV (why didn't they just use CSV or
TAB delimited?) and the data fields are decimal ASCII. The fields are
terminated by zero bytes. There is no newline or other record terminator, so
you must keep count of fields read and insert record breaks.

START OF FILE

ASCII first heading identifies the Foxwell program, ends with a zero byte.

ASCII second heading identifies the run mode, ends with a zero byte.

Eight byte sequence 7b 14 8e 3f 00 00 00 00, purpose unknown, skipped.

ASCII third header, specifies program parameters, ends with a zero byte.

Number of fields, two bytes, least-significant byte first.

List of field names, each one comprising:

    Possibly a ten-byte sequence beginning with 06. If an 06 is found,
    skip ten bytes. This is present in OBD2 but not Honda. It has a
    counting byte which may be the OBD2 data field number.
    
    Field name, ends with a zero byte.

    Unit of measure, ends with a zero byte.
    Hex B0 represents a degree symbol.

    Unit may be an empty string but will always have a zero byte.
    There will be two zero bytes per field name, not including those
    embedded in the ten-byte sequence starting with 06.

    The number of field names will correspond to the number of fields.
    There is no end marker.

Table of data, ASCII strings terminated by null bytes. There is no marker at
the end of a line. You must count fields. 

Four-byte count of lines, least-signficant byte first.
End of file marker: hex aa 55 33 11.
Possble CR-LF hex 0d 0a, seen on Honda but not OBD2.

END OF FILE

To read the records you must count columns to determine where one record ends
and the next begins. To detect end of file, when you detect the zero byte at
the end of the last column of a record, look ahead four bytes for the aa 55 33
11 mark.

46 00 bd 00 00 00 aa 55 33 11 0d 0a
^^ last character of last column
   ^^ zero byte of last column
      ^^ ^^ ^^ ^^ line counter
                  ^^ ^^ ^^ ^^ end marker


"""

import sys

def parse_cbf(cbf):
	headings = [ ]
	header = [ ]
	data = [ ]
	errors = [ ]
	flen = len(cbf)
	fp = 0

	# Read the top headings
	ft = ''
	while cbf[fp] != "\x00":
		ft += cbf[fp]
		fp += 1
		if fp >= flen:
			errors.append("end of file during heading 1 parse")
			return headings,header,data,errors
	headings.append(ft)
	ft = ''
	fp += 1
	while cbf[fp] != "\x00":
		ft += cbf[fp]
		fp += 1
		if fp >= flen:
			errors.append("end of file during heading 2 parse")
			return headings,header,data,errors
	headings.append(ft)
	ft = ''
	# skip null plus eight bytes which are normally 7b 14 8e 3f 00 00 00 00
	fp += 9
	while cbf[fp] != "\x00":
		ft += cbf[fp]
		fp += 1
		if fp >= flen:
			errors.append("end of file during heading 3 parse")
			return headings,header,data,errors
	headings.append(ft)
	fp += 1
	
	# Number of fields is a little-endian 16 bit binary number
	num_fields = ord(cbf[fp]) + 256*ord(cbf[fp+1]) 
	fp += 2

	# Read the tabular data header
	fn = 0
	ft = ''
	nz = 0
	while fn < num_fields:
		if fp >= flen:
			errors.append("end of file during header parse")
			break
		if cbf[fp] == "\x00" and nz > 0: # header field break on 2nd zero for obd2
			ft = ft.replace("\xb0","deg ").rstrip(' ')
			if len(ft) > 0:
				header.append(ft)
				fn += 1
			fp += 1
			ft = ''
			nz = 0
		elif cbf[fp] == "\x06": # start-of-field header for obd2
			fp += 10 # skip ten bytes
		elif cbf[fp] != "\x00":
			if ord(cbf[fp]) > 31:
				ft += cbf[fp]
			fp += 1
		else: # zero
			nz += 1
			if len(ft) > 0:
				ft += ' '
			fp += 1
	
	if len(errors) > 0:
		return headings,header,data,errors
	
	# Read the tabular data
	read_records = 0
	expected_records = -1
	while fp < flen:
		# Parse a data line
		fn = 0
		ft = ''
		dataline = [ ]
		while fn < num_fields:
			if fp >= flen:
				errors.append("end of file during data parse")
				break
			if cbf[fp] == "\x00":
				dataline.append(ft)
				fp += 1
				fn += 1
				ft = ''
			else:
				ft += cbf[fp]
				fp += 1
		if fn == num_fields:
			data.append(dataline)
			read_records += 1
			if cbf[fp+4] == "\xaa" and cbf[fp+5] == "\x55" and cbf[fp+6] == "\x33" and cbf[fp+7] == "\x11": # eof mark
				expected_records = ord(cbf[fp+0]) + 256*ord(cbf[fp+1]) + 65536*ord(cbf[fp+2]) + 16777216*ord(cbf[fp+3])
				break
	if read_records != expected_records:
		errors.append("read " + str(read_records) + " records but expected " + str(expected_records) + " records")
	return headings,header,data,errors

# Excel-style quote doubling
def format_csv_field(f):
	if f.find('"') >= 0:
		return '"' + f.replace('"','""') + '"'
	elif f.find(',') >= 0:
		return '"' + f + '"'
	else:
		return f
	
def print_csv(header,data):
	csvfile = [ header ]
	csvfile.extend(data)
	for l in csvfile:
		lout = ''
		for f in l:
			f = f.strip(' ')
			if len(lout) == 0:
				lout = format_csv_field(f)
			else:
				lout += ',' + format_csv_field(f)
		print lout

if len(sys.argv) < 2:
	print "specify file name"
	sys.exit(1)
fp = open(sys.argv[1],"rb")
cbf_in = fp.read()
fp.close()
headings,header,data,errors = parse_cbf(cbf_in)
for l in headings:
	print l
if len(errors) > 0:
	for l in errors:
		print "Error:",l
print_csv(header,data)

# EOF
