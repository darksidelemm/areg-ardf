#!/usr/bin/env python
#
#   AREG ARDF GPS Handler
#
#   This script listens to a GPS, and pulls out the required sentences and data.
#   These are then passed onto the ARDF suite, which requires GPGGA and GPVTG sentences
#    
#    Copyright (C) 2013 Mark Jessop <mark.jessop@adelaide.edu.au>
# 
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
# 
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
#      GNU General Public License for more details.
# 
#      For a full copy of the GNU General Public License, 
#      see <http://www.gnu.org/licenses/>.

import socket,ARDF,sys,serial

# NMEA Checksum - Checksum of data, not including first $.
def nmea_checksum(sentence):
    calc_cksum = 0
    for s in sentence:
        calc_cksum ^= ord(s)
    return "*%02X\r\n" % calc_cksum

# Generate a GPVTG string from a collected data bearing.
def generate_GPVTG(true_bearing, declination):
    vtg = "GPVTG,%03d,T,%03d,M,00.0,N,00.0,K" % (int(true_bearing),int(true_bearing-declination)%360)
    return "$" + vtg + nmea_checksum(vtg)


UDP_IP = "255.255.255.255" # Broadcast address
UDP_PORT = 2004
sensorid = 1 # GPS Source

serialport = 5 #"/dev/tty.usbserial"
serialbaud = 4800

velocity_threshold = 30 # Velocity threshold in kph

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

sequence = 0
true_bearing = 0.0 # True bearing
declination = 8.0 # Magnetic Variation/Declination 
magnetometer_override = False

ser = serial.Serial(serialport,serialbaud,timeout=5)

while True:
    line = ser.readline()
    
    try:
        nmea_type = line[1:6]
        
        if nmea_type == "GPGGA":
            # Pass through GPGGA strings
            
            print "Sending: " + line
            gpvtg = generate_GPVTG(true_bearing,declination)
            print "Sending: " + gpvtg
            
            # Send via UDP
            gpgga_msg = ARDF.TMessage("GPS_",sensorid,sequence,line)
            sequence = sequence + 1
            gpvtg_msg = ARDF.TMessage("GPS_",sensorid,sequence,gpvtg)
            sock.sendto(gpgga_msg.to_string(), (UDP_IP,UDP_PORT))
            sock.sendto(gpvtg_msg.to_string(), (UDP_IP,UDP_PORT))
            sequence = sequence + 1
        elif nmea_type == "GPRMC":
            # Attempt to parse a GPRMC string, and gate the bearing if
            # the vehicle velocity is above our threshold
            gprmc = line.split('r')
            if len(gprmc) == 13:
                velocity = float(gprmc[7])*1.82
                declination = float(gprmc[10])
                if gprmc[11] == "W":
                    declination = declination*-1.0
                    
                if velocity > velocity_threshold and magnetometer_override == False:
                    true_bearing = int(gprmc[8])
                    print "Gating bearing of " + str(true_bearing)
        
        elif nmea_type == "HCHDG":
            # Holy crap, this GPS has a magnetometer in it!
            # Use the magnetometers bearing instead of the gps bearing
            magnetometer_override = True
            
            hchdg = line.split(',')
            if len(hchdg) == 6:
                declination = float(hchdg[4])
                if hchdg[5][0] == 'W':
                    declination = declination * -1.0
                true_bearing = int(hchdg[1]) + declination
        
        else:
            # Sentence we dont care about.
            pass
      
    except:
        print "Invalid line"