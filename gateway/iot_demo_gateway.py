#   Simple IOT demo in Linux
#   Copyright (C) 2019  Jeune Prime M. Origines <primeyo2004@yahoo.com>

#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

#!/usr/bin/env python3

import bleclient
import tc74

import dbus
import sys
from dbus.mainloop.glib import DBusGMainLoop

import time
import uuid
import ibmiotf.gateway
import ibmiotf.device


try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject


I2C_BUS            = 1
TC74_I2C_ADDRESS   = 0x4a
TC74_READ_INTERVAL = 3000


#   IOT_ORGANIZATION = ""
#   IOT_GATEWAYTYPE  = ""
#   IOT_GATEWAYID    = ""
#   IOT_AUTHMETHOD   = ""
#   IOT_AUTHTOKEN    = ""


# ---------------------------------------------------------


class SimpleGatewayImpl:

    IOT_DEVICE_SENSOR_TYPE   = "DEMOSENSOR_T"
    IOT_DEVICE_SENSOR_ID     = "TEMPSENSOR_1"
    IOT_DEVICE_ACTUATOR_TYPE = "DEMOACTUATOR_T"
    IOT_DEVICE_ACTUATOR_ID   = "ITAG_ALARM_1"
    IOT_EVENT_READING        = "reading"
    IOT_EVENT_CURRENT_STATE  = "current_state"
    IOT_CMD_NEW_STATE        = "new_state"
 
    def __init__(self, temp_sensor, itag_device, iot_gateway):
        self.sensorDevice   = temp_sensor
        self.actuatorDevice = itag_device
        self.iotGateway     = iot_gateway

    def Start(self):
        stateData = {'alarm' : 0}
        self.iotGateway.publishDeviceEvent(self.IOT_DEVICE_ACTUATOR_TYPE, self.IOT_DEVICE_ACTUATOR_ID, self.IOT_EVENT_CURRENT_STATE, "json", stateData, qos=1, on_publish=self.__PublishActuatorCallback)

        self.iotGateway.subscribeToDeviceCommands(deviceType=self.IOT_DEVICE_ACTUATOR_TYPE, deviceId=self.IOT_DEVICE_ACTUATOR_ID, command=self.IOT_CMD_NEW_STATE,format='json',qos=2)
        self.iotGateway.deviceCommandCallback = self.__ActuatorCommandHandler

        GObject.timeout_add(TC74_READ_INTERVAL,self.__SensorReadHandler)

   
    def __SensorReadHandler(self):
        value = self.sensorDevice.read()
        print ('Read temperature:', int(value))
        print ('Publishing temperature reading.')

        readingData = {'temperature' : value}
        deviceSuccess = self.iotGateway.publishDeviceEvent(self.IOT_DEVICE_SENSOR_TYPE, self.IOT_DEVICE_SENSOR_ID, self.IOT_EVENT_READING, "json", readingData, qos=1, on_publish=self.__PublishSensorCallback)
        
        if not deviceSuccess:
            print("Gateway not connected to IBM Watson IoT Platform while publishing from Gateway on behalf of a device")
    
        return True

    def __PublishSensorCallback(self):
        print('Publish temperature reading successful!')

    def __ActuatorCommandHandler(self,command):
        print("Id = %s (of type = %s) received the device command %s at %s" % (command.id, command.type, command.data, command.timestamp))
        print("Setting ITAG Alarm to: ", command.data['alarm'])

    def __PublishActuatorCallback(self):
        print('Publish actuator successful!')

    def __ItagReadValueCallback(self, value):
        if len(value) > 0:
            stateData = {'alarm' : value[0]}
            self.iotGateway.publishDeviceEvent(self.IOT_DEVICE_ACTUATOR_TYPE, self.IOT_DEVICE_ACTUATOR_ID, self.IOT_EVENT_CURRENT_STATE, "json", stateData, qos=1, on_publish=self.__PublishActuatorCallback)
    def __ItagWriteValueCallback(self):
        # read the new ITAG value here
        pass







def main():

    print('Starting demo gateway...')

    # Initialize Dbus Main Loop
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    mainloop = GObject.MainLoop()

    sensorDevice   = None
    actuatorDevice = None
    iotGateway     = None


    # Initialize the TC74 temperature sensor
    try:
        sensorDevice = tc74.create_TC74Sensor('TC74SensorDummy',I2C_BUS,TC74_I2C_ADDRESS)
    except Exception as ex:
        if type(ex) == OSError and ex.errno == 121:
            print('Failed to initialize TC74 sensor',file=sys.stderr) 
        else:
            print(ex, file=sys.stderr) 
        sys.exit(1) 
           

    # Fetch the ITAG BLE Alarm
    #bleclient.FetchDevices(bus, my_cb)
    #if len(bluezdevs) == 0:
    #    print ('Unable to find the connected ITAG device.',file=sys.stderr)
    #    sys.exit(1) 


    # Connect to IBM Watson IOT Platform
    try:
            # Use iot_demo_gateway.cfg for configuration
            #   iotGatewayOptions = {"org"           : IOT_ORGANIZATION, 
            #                        "type"          : IOT_GATEWAYTYPE, 
            #                         "id"           : IOT_GATEWAYID, 
            #                         "auth-method"  : IOT_AUTHMETHOD, 
            #                         "auth-token"   : IOT_AUTHTOKEN}
            iotGatewayOptions   = ibmiotf.device.ParseConfigFile('./iot_demo_gateway.cfg')
            iotGateway        = ibmiotf.gateway.Client(iotGatewayOptions)
            iotGateway.connect()
    except Exception as e:
            print("Caught exception connecting device: %s" % str(e))
            sys.exit()



    gatewayImpl = SimpleGatewayImpl(sensorDevice, actuatorDevice, iotGateway)
    gatewayImpl.Start()


    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()

    iotGateway.disconnect()
    print('Exiting demo gateway...')

if __name__ == '__main__':
    main()


