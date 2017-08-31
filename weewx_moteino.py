# Weewx module to read pressure / temp from a moteino device and log the associated pressure / temp.
# (c) 2017 Paul McAvoy <paulmcav@gmail.com>
#
# Currently tested with Weewx 3.7.1
# This file belongs in the associated /home/weewx/bin/user folder
#
# To enable this module, add the following line(s) to your weewx.conf file:
#
# [Engine]
#     [[Services]]
#         data_services = user.moteino.MoteinoService
#
# Additionally, you can put your serial port communication settings in the config file or hardcode below:
#
# [MoteinoService]
#        port = /dev/ttyUSB0
#        speed = 115200
#        timeout = 2
#        mode = E
#

import time
import serial
import re
#import httplib
import syslog

import weewx
from weewx.wxengine import StdService

DEFAULT_DEV='/dev/ttyUSB0'
DEFAULT_SPEED=115200
DEFAULT_TIMEOUT=2
DEFAULT_MODE='E'    # E / M

# TODO: look at configuration to determine if mode should be metric or english units

#dev='/dev/cu.usbserial-DA01IDU2'

# weather station service - sensor measurement
SERVICE_NAME = "Moteino"
SERVICE_VERSION = "1.1"

class MoteinoService(StdService):

    def poll_moteino(self, Mode=DEFAULT_MODE):
        try:
            with serial.Serial(self.port, self.speed,timeout=self.timeout) as ser:
                # look for init string: "BMP180 init OK"
                m_line = ser.readline()
                # obtain metric measurement: 66%H 81.82 F 29.56 inHg_abs  29.78 inHg_rel
                ser.write(Mode)
                m_line = ser.readline()
#                print "poll_moteino(%s): %s" % (Mode, m_line)
#                syslog.syslog(syslog.LOG_DEBUG, "moteino: poll %s" % m_line)
#                syslog.syslog(syslog.LOG_INFO, "moteino: poll %s" % m_line)

            # Read successfull, regeg string for interesting info
            #regex="(\d+)%H\s(\d+.\d+) F\s(\d+.\d+) inHg"	# English units
            regex="(\S+)\s(\S+)\s(\S+)\s(\S+)"			# Metric units
            m = re.match( regex, m_line )

#            print "H: %s, F: %s, P: %s" % ( m.group(1), m.group(2), m.group(3) )
            return ( m_line, m.group(1), m.group(2), m.group(3) )

        except Exception, e:
#            print "motino error: ", e
            syslog.syslog(syslog.LOG_ERR, "moteino: error: %s" % e)
            return ('-', 0.0, 0.0, 1013.25 )	# 29.92 / 1013.25 (baseline baro pressure)

    def __init__(self, engine, config_dict):
        super(MoteinoService, self).__init__(engine, config_dict)

        d = config_dict.get('MoteinoService', {})
        
        self.port = d.get('port',DEFAULT_DEV)
        self.speed = int(d.get('speed',DEFAULT_SPEED))
        self.timeout = int(d.get('timeout',DEFAULT_TIMEOUT))
        self.mode = d.get('mode',DEFAULT_MODE)

        syslog.syslog(syslog.LOG_INFO, "moteino: using %s,%d,%d,%s" % (self.port, self.speed, self.timeout, self.mode))

	m = self.poll_moteino()
        print "moteino: %s>> H: %s, F: %s, P: %s" % ( m[0], m[1], m[2], m[3] )
        syslog.syslog(syslog.LOG_INFO, "moteino: %s" % m[0])

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.newArchiveRecord)
        self.bind(weewx.NEW_LOOP_PACKET, self.newLoopPacket)

    def newLoopPacket(self, event):
        """This function is called on each new LOOP packet."""
	m = self.poll_moteino('M')

#        print "Lunits: ",event.packet
# Lunits:  {'status': 0, 'delay': 4, 'outTempBatteryStatus': 0, 'outTemp': 16.5, 'outHumidity': 70.0, 'UV': None, 'radiation': None, 'rain': None, 'dateTime': 1500089435, 'windDir': 90.0, 'pressure': 0.0, 'windSpeed': 1.0800000000000003, 'inHumidity': 63.0, 'inTemp': 22.3, 'rxCheckPercent': 100, 'windGust': 2.5200000000000005, 'rainTotal': 69.99, 'ptr': 928, 'usUnits': 16}

#        print "moteino_read: %s>> H: %s, F: %s, P: %s" % ( m[0], m[1], m[2], m[3] )
#        syslog.syslog(syslog.LOG_INFO, "moteino_read: (%s)  %s" % (self.mode, m[0]) )

        event.packet['barometer'] = float(m[3])
        event.packet['pressure'] = float(m[3])

    def newArchiveRecord(self, event):
        """This function is called on each new ARCHIVE record."""
	m = self.poll_moteino()

#        print "Aunits: ",event.record
# AUnits:  {'status': 0, 'delay': 10, 'outTempBatteryStatus': 0, 'interval': 10, 'outTemp': 16.400000000000002, 'outHumidity': 69.0, 'UV': None, 'radiation': None, 'rain': None, 'dateTime': 1500089139, 'windDir': 0.0, 'pressure': 0.0, 'windSpeed': 0.0, 'inHumidity': 63.0, 'inTemp': 22.3, 'rxCheckPercent': 100, 'windGust': 0.0, 'rainTotal': 69.99, 'ptr': 912, 'usUnits': 16}

#        print "moteino_read: %s>> H: %s, F: %s, P: %s" % ( m[0], m[1], m[2], m[3] )
#        syslog.syslog(syslog.LOG_INFO, "moteino_read: (%s)  %s" % (self.mode, m[0]) )

        event.record['extraHumid1'] = float(m[1])
        event.record['extraTemp1'] = float(m[2])
        event.record['extraTemp2'] = float(m[3])
        event.record['barometer'] = float(m[3])
        event.record['pressure'] = float(m[3])

