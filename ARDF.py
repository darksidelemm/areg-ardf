#!/usr/bin/env python
#
#   AREG ARDF Library
#
#   This library provides message formats and classes to talk to the AREG
#   DF System.
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

import struct

# TMessage Class, from rdfcommon.h
class TMessage:

    length = 0

    def __init__(self,ident,type,seq,data):
        self.ident = ident
        self.type = int(type)
        self.seq = int(seq)
        self.data = data
        
    def to_string(self):
        self.length = len(self.data)
        
        if len(self.ident) > 4:
            self.ident = self.ident[:4]
        
        output = struct.pack("4sI",self.ident,self.type) + struct.pack("!HH",self.seq,self.length)
        return output + self.data
        
class DF_Bearing:
    
    bearing = 0
    callsign = "VK5ARG"
    sensorid = 3
    sequenceno = 0
    
    def __init__(self,call="VK5ARG",bearing=0,sensorid=3,sequenceno = 0):
        self.bearing = bearing%360
        self.callsign = call
        self.sensorid = sensorid
        self.sequenceno = sequenceno
        
    def emit(self):
        bearing_string = "%03d" % self.bearing
        tx_message = self.callsign + ">APRS:%" + bearing_string + "/8"
        msg = TMessage("GPS_",self.sensorid,self.sequenceno,tx_message)
        return msg.to_string()
        
        
