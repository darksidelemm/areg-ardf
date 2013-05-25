#!/usr/bin/env python
#
#   AREG ARDF BPI Emulator - O'Clock Edition
#
#   This script emulates the function of a beam position indicator.
#   Bearings entered must be relative to the front of the car.
#   Bearings are entered as clock hour-hand positions
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
#
#

import socket,ARDF,sys

UDP_IP = "255.255.255.255"
UDP_PORT = 2006
sensorid = 3 # Usually the Front BPI

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

sequence = 0
print "ARDF BPI Emulator"
print "Press q to quit."

while True:
    print "O'Clock Bearing relative to car:",
    input = raw_input()
    
    if input == "q":
        sys.exit(0)
    
    bearing = 0
    
    try:
        bearing = (int(input)%12)*30
        if bearing <= 360 and bearing >=0:
            msg = ARDF.DF_Bearing(bearing=bearing,sequenceno=sequence,sensorid=sensorid)
            print msg.emit()
            sock.sendto(msg.emit(), (UDP_IP,UDP_PORT))
            sequence = sequence + 1
    except:
        print "Invalid bearing"
