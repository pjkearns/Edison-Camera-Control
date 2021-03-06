import sys
import os
import re
import socket
import time
from ant.core import driver, node, event, message, log
from ant.core.constants import CHANNEL_TYPE_TWOWAY_RECEIVE, TIMEOUT_NEVER
from settings import camaddr
from settings import camport

count = 0
this_hr = 0
last_hr = 0

print("would you like Photo(1) or Video(2) modes?")
cam_mode = int(raw_input("> "))


print("Input threshold heart rate.")
threshold = int(raw_input("> "))

class HRM(event.EventCallback):

    def __init__(self, serial, netkey):
        self.serial = serial
        self.netkey = netkey
        self.antnode = None
        self.channel = None

    def start(self):
        print("starting node")
        self._start_antnode()
        self._setup_channel()
        self.channel.registerCallback(self)
        print("start listening for hr events")

    def stop(self):
        if self.channel:
            self.channel.close()
            self.channel.unassign()
        if self.antnode:
            self.antnode.stop()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.stop()

    def _start_antnode(self):
        stick = driver.USB2Driver(self.serial)
        self.antnode = node.Node(stick)
        self.antnode.start()

    def _setup_channel(self):
        key = node.NetworkKey('N:ANT+', self.netkey)
        self.antnode.setNetworkKey(0, key)
        self.channel = self.antnode.getFreeChannel()
        self.channel.name = 'C:HRM'
        self.channel.assign('N:ANT+', CHANNEL_TYPE_TWOWAY_RECEIVE)
        self.channel.setID(120, 0, 0)
        self.channel.setSearchTimeout(TIMEOUT_NEVER)
        self.channel.setPeriod(8070)
        self.channel.setFrequency(57)
        self.channel.open()

    def process(self, msg):
        global count
	global cam_mode
	global threshold


	global this_hr
	global last_hr
	if isinstance(msg, message.ChannelBroadcastDataMessage):
            print("heart rate is {}".format(ord(msg.payload[-1])))
	    this_hr = int(ord(msg.payload[-1]))
	    if cam_mode == 1 and this_hr >= threshold:
		count += 1
		if count % 5 == 0:
			srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			srv.connect((camaddr, camport))

			srv.send('{"msg_id":257,"token":0}')

			data = srv.recv(512)
			if "rval" in data:
				token = re.findall('"param": (.+) }',data)[0]	
			else:
				data = srv.recv(512)
				if "rval" in data:
					token = re.findall('"param": (.+) }',data)[0]	


			tosend = '{"msg_id":769,"token":%s}' %token
			srv.send(tosend)
			srv.recv(512)
		
	    elif cam_mode == 2 and this_hr >= threshold and last_hr < threshold:
		
                
		
                 
					print("this should start video")                 
                                        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    					srv.connect((camaddr, camport))
    					srv.send('{"msg_id":257,"token":0}')
    					data = srv.recv(512)
    					if "rval" in data:
	    					token = re.findall('"param": (.+) }',data)[0]
    					else:
	    					data = srv.recv(512)
	    					if "rval" in data:
		    					token = re.findall('"param": (.+) }',data)[0]
    					tosend = '{"msg_id":513,"token":%s}' %token
    					srv.send(tosend)
    					srv.recv(512)
                                	print("Recording")
            
	    elif cam_mode == 2 and this_hr < threshold and last_hr >= threshold:
		
		
                			print("This should stop video")
                
                
                
                                        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        srv.connect((camaddr, camport))
                                        srv.send('{"msg_id":257,"token":0}')
                                        data = srv.recv(512)
                                        if "rval" in data:
                                                token = re.findall('"param": (.+) }',data)[0]
                                        else:
                                                data = srv.recv(512)
                                                if "rval" in data:
                                                        token = re.findall('"param": (.+) }',data)[0]
                                        tosend = '{"msg_id":514,"token":%s}' %token
                                        srv.send(tosend)
                                        srv.recv(512)
                                        print("Stopped")

   	    last_hr = this_hr                       
 



SERIAL = '/dev/ttyMFD2'
NETKEY = 'B9A521FBBD72C345'.decode('hex')

with HRM(serial=SERIAL, netkey=NETKEY) as hrm:
    hrm.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)
   