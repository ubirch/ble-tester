import struct
import sys

import msgpack
from bluepy.btle import UUID, Peripheral, DefaultDelegate, Scanner


rx_data = [] # = ""
process_data = 0

def handleMSGPACK():
    print "process_data"
    # newString = ''.join(rx_data)
    # print newString
    unpacker = msgpack.Unpacker(rx_data)
    for unpacked in unpacker:
        print unpacked


class MyDelegate(DefaultDelegate):
    #Constructor (run once on startup)  
    def __init__(self, params):
        DefaultDelegate.__init__(self)
      
    #func is caled on notifications

    # process the received data here
    def handleNotification(self, cHandle, data):
        # print ("Notification from Handle: 0x" + format(cHandle,'02X') + " Value: "+ format(ord(data[0])))
        # for i in data
        if "NONE\r\n" in str(data):
            # print "none man"
            # for i in data:
            #     rx_data += str(i)
            process_data = True
        # elif "start\r\n" in str(data):

            # print "start man " + str(data)

        else:
            process_data = True
            # print data
            rx_data.append(str(data)) # += str(data)
            # print rx_data

newData = ""
def joinData():
    newData = ''.join(rx_data)
    # newData = tempdata
    rx_data[:] = []
    # newData.join(rx_data.pop(0))
    # nelems = unpacker.read_map_header()

    # unpacker = msgpack.Unpacker(newData)
    # for unpacked in unpacker:
    #     print unpacked
    print newData

# Trackle Service and Char UUIDs
UART_service_uuid = UUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
UART_rx_char_uuid    = UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
UART_tx_char_uuid    = UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e")

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

deviceIndex = 1
# deviceIndex = int(input("Input the device Index:"))
# if 0 > deviceIndex > 10:

print deviceIndex
print scanDeviceList[deviceIndex]

trackleBLE = "e0:87:40:09:11:ea"
# p = Peripheral(scanDeviceList[deviceIndex], "random")
p = Peripheral(trackleBLE, "random")
p.setDelegate( MyDelegate(p) )

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
        print ("Button1 Client Characteristic Configuration found at handle 0x"+ format(desriptor.handle,"02X"))
        hButtonCCC=desriptor.handle
 
# Turn notifications on by setting bit0 in the CCC more info on:
# https://developer.bluetooth.org/gatt/descriptors/Pages/DescriptorViewer.aspx?u=org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml    
p.writeCharacteristic(hButtonCCC, struct.pack('<bb', 0x01, 0x00))
print "Notification is turned on for Button1"


# Main loop --------
while True:
    if p.waitForNotifications(1.0):
        # handleNotification() was called
        continue

    # print process_data
    if process_data:
        # print "process_data"
        # newString = ''.join(rx_data)
        # print newString
        unpacker = msgpack.Unpacker(rx_data)
        for unpacked in unpacker:
            print unpacked
        process_data = False
    else:
        # print process_data
        joinData()
        # print rx_data
        # print "Waiting... Waited more than one sec for notification"
        # Perhaps do something else here
