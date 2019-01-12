```Parse Foxwell Tech cbf file into csv
Version 0.1 for python 2.7
Mike Ingle <inglem@pobox.com>
This code is in the public domain.

This program is available as a web service at:
https://www.confidantmail.org/parse_cbf_web.html

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
```
