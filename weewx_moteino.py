# Weewx module to read pressure / temp from a moteino device and log the associated pressure / temp.
# (c) 2017 Paul McAvoy <paulmcav@gmail.com>

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
DEFAULT_MODE='M'

#dev='/dev/cu.usbserial-DA01IDU2'

DRIVER_NAME = "Moteino"
DRIVER_VERSION = "1.1"

class MoteinoService(StdService):

    def poll_moteino(self):
        try:
            with serial.Serial(self.port, self.speed,timeout=self.timeout) as ser:
                # look for init string: "BMP180 init OK"
                m_line = ser.readline()
                # obtain metric measurement: 66%H 81.82 F 29.56 inHg_abs  29.78 inHg_rel
                ser.write(self.mode)
                m_line = ser.readline()
#                print "poll_moteino(%s): %s" % (self.mode, m_line)
#                syslog.syslog(syslog.LOG_DEBUG, "moteino: %s" % m_line)
#                syslog.syslog(syslog.LOG_INFO, "moteino: %s" % m_line)

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

        self.bind(weewx.NEW_ARCHIVE_RECORD, self.read_moteino)
	# TODO: look into LOOP process to read baro pressure

    def read_moteino(self, event):
	m = self.poll_moteino()

#        print "units: ",event.record
#        print "moteino_read: %s>> H: %s, F: %s, P: %s" % ( m[0], m[1], m[2], m[3] )
#        syslog.syslog(syslog.LOG_INFO, "moteino_read: %s" % m[0])

        event.record['extraHumid1'] = float(m[1])
        event.record['extraTemp1'] = float(m[2])
        event.record['extraTemp2'] = float(m[3])
        event.record['barometer'] = float(m[3])

