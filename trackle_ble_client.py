# !/usr/bin/env python

# Author: Niranjan Rao

import struct
import time
import msgpack
import requests
from bluepy.btle import UUID, Peripheral, DefaultDelegate, Scanner
from StringIO    import StringIO

mydata = StringIO()

HTTP_POST_URL = 'http://192.168.150.103:8080/api/avatarService/v1/device/update/mpack'

def unpack_msgpack():
    """
    Unpack the msgpack data and print it
    """
    print "Unpack Temperature Values..."

    thestr =  StringIO(mydata.getvalue())
    unpacker = msgpack.Unpacker(thestr)

    for val in unpacker:
        print val
    print "All the sensor values unpacked..."


def send_data_to_backend():
    """
    Sends the msgpack binary data to the backend
    """
    thestr =  StringIO(mydata.getvalue())
    post_response = requests.post(url=HTTP_POST_URL, data=thestr)
    print "HTTP Response:" + str(post_response)
    mydata.close()


class MyDelegate(DefaultDelegate):
    readData = False
    #Constructor (run once on startup)
    def __init__(self, params):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        # print ("Notification from Handle: 0x" + format(cHandle,'02X') + " Value: "+ format(ord(data[0])))
        hexstr = data
        newhexstr = ':'.join(x.encode('hex') for x in hexstr)
        print newhexstr

        if 'No more data' in data:
            print "No data t0 send..."
            self.readData = True

        elif 'OK let me sleep...' in data:
            print "Trackle is going to sleep..."

        elif "\r\n\r\n" in data:
            print'newline .....'

            lfhex = data
            newlfhex = ':'.join(x.encode('hex') for x in lfhex)
            print newlfhex

            newData = data[:-4]
            mydata.write(newData)

            lfhex = newData
            newlfhex = ':'.join(x.encode('hex') for x in lfhex)
            print newlfhex

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

p = Peripheral(scanDeviceList[deviceIndex], "random")
pq = MyDelegate(p)
p.setDelegate(pq)

#Get UART Service
UARTService=p.getServiceByUUID(UART_service_uuid)
# Get The UART-Characteristics
UARTC=UARTService.getCharacteristics(UART_rx_char_uuid)[0]
#Get The handle the  UART-Characteristics
hUARTC=UARTC.getHandle()
# Search and get Get The UART-Characteristics "property" (UUID-0x2902 CCC-Client Characteristic Configuration))
#  wich is located in a handle in the range defined by the boundries of the UARTService
for desriptor in p.getDescriptors(hUARTC):  # The handle range should be read from the services
   if (desriptor.uuid == 0x2902):                   #      but is not done due to a Bluez/BluePy bug :(     
        print ("Trackle UART Client Characteristic Configuration found at handle 0x"+ format(desriptor.handle,"02X"))
        hUARTCCC=desriptor.handle
 
# Turn notifications on by setting bit0 in the CCC more info on:
# https://developer.bluetooth.org/gatt/descriptors/Pages/DescriptorViewer.aspx?u=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml    
p.writeCharacteristic(hUARTCCC, struct.pack('<bb', 0x01, 0x00))
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