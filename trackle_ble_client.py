# !/usr/bin/env python

import struct
import time
import socket
import msgpack
import requests
from bluepy.btle import UUID, Peripheral, DefaultDelegate, Scanner
from StringIO    import StringIO

TCP_IP = 'http://192.168.150.103:8080/api/avatarService/v1/device/update/mpack'
TCP_PORT = 8080
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

mydata = StringIO()

def unpack_msgpack():
    print "Unpack Temperature Values..."
    thestr =  StringIO(mydata.getvalue())
    # print thestr
    # print "hello"
    # hexstr = ':'.join(x.encode('hex') for x in thestr)
    # print hexstr

    unpacker = msgpack.Unpacker(thestr)

    for val in unpacker:
        print val
    print "All the sensor values unpacked..."


def send_data_to_backend():

    # post_data = {'username': 'joeb', 'password': 'foobar'}
    # POST some form-encoded data:
    thestr =  StringIO(mydata.getvalue())
    post_response = requests.post(url=TCP_IP, data=thestr)
    print post_response
    # get_response = requests.get(url=TCP_IP)
    # print get_response
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # # s.connect((TCP_IP, TCP_PORT))
    # s.connect(TCP_IP)
    # s.send(mydata.getvalue())
    # data = s.recv(BUFFER_SIZE)
    # s.close()
    # print "received data:", data
    # mydata.close()

class MyDelegate(DefaultDelegate):
    readData = False
    #Constructor (run once on startup)
    def __init__(self, params):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        # print ("Notification from Handle: 0x" + format(cHandle,'02X') + " Value: "+ format(ord(data[0])))
        print data
        if 'No more data' in data:
            print "No data tp send..."
            self.readData = True

        if 'OK let me sleep...' in data:
            print "Trackle is going to sleep..."

        elif "\r\n\r\n" in data:
            newData = data[:-4]
            mydata.write(newData)
            print newData

        else:
            mydata.write(data)

    def getTxflag(self):
        return self.readData

# ++++++++++++++++++++++++++++++ BLE START ++++++++++++++++++++++++++++
# Trackle Service and Char UUIDs
UART_service_uuid    = UUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
UART_rx_char_uuid    = UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
UART_tx_char_uuid    = UUID("6e400002-b5a3-f393-e0a9-e50e24dcca9e")

# Init the scanner
scanner = Scanner()
# Start scan, pass the timeout as scan variable
devices = scanner.scan(4.0)

scanDeviceList = []
addCount = 0
for dev in devices:
    print " %d. Device %s (%s), RSSI=%d dB" % (addCount, dev.addr, dev.addrType, dev.rssi)
    addCount += 1
    scanDeviceList.append(dev.addr)
    for (adtype, desc, value) in dev.getScanData():
        print "  %s = %s" % (desc, value)

# deviceIndex = 1
deviceIndex = int(input("Input the device Index:"))

# print deviceIndex
print scanDeviceList[deviceIndex]

# trackleBLE = "c2:bf:e4:96:9e:4b"
# trackleBLE  = "e0:87:40:09:11:ea"
p = Peripheral(scanDeviceList[deviceIndex], "random")
# p = Peripheral(trackleBLE, "random")
pq = MyDelegate(p)
p.setDelegate(pq)
# p.setDelegate( MyDelegate(p))

#Get ButtonService
ButtonService=p.getServiceByUUID(UART_service_uuid)
# Get The Button-Characteristics
ButtonC=ButtonService.getCharacteristics(UART_rx_char_uuid)[0]
#Get The handle tf the  Button-Characteristics
hButtonC=ButtonC.getHandle()
# Search and get Get The Button-Characteristics "property" (UUID-0x2902 CCC-Client Characteristic Configuration))
#  wich is located in a handle in the range defined by the boundries of the ButtonService
for desriptor in p.getDescriptors(hButtonC):  # The handle range should be read from the services
   if (desriptor.uuid == 0x2902):                   #      but is not done due to a Bluez/BluePy bug :(     
        print ("Trackle UART Client Characteristic Configuration found at handle 0x"+ format(desriptor.handle,"02X"))
        hButtonCCC=desriptor.handle
 
# Turn notifications on by setting bit0 in the CCC more info on:
# https://developer.bluetooth.org/gatt/descriptors/Pages/DescriptorViewer.aspx?u=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml    
p.writeCharacteristic(hButtonCCC, struct.pack('<bb', 0x01, 0x00))
print "Notification is turned on for Trackle sensor"

# ++++++++++++++++++++++++++++++ BLE STOP  ++++++++++++++++++++++++++++

while True:
    if p.waitForNotifications(1.0):
        # handleNotification() was called
        continue

    if pq.getTxflag() is True:
        time.sleep(0.5)
        print "Read the Trackle data..."
        pq.readData = False
        unpack_msgpack()
        send_data_to_backend()
    else:
        print '...'

    # send_data_to_backend()
        # print "Waiting... Waited more than one sec for notification"