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


import sys
import time
import uuid
import json
import ibmiotf.application

try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject


#   IOT_ORGANIZATION   = ""
#   IOT_APPID          = ""
#   IOT_AUTHMETHOD     = ""
#   IOT_AUTHKEY        = ""
#   IOT_AUTHTOKEN      = ""

# ---------------------------------------------------------


class SimpleControlApplicationImpl:

    IOT_DEVICETYPE_ANY = "+"
    IOT_DEVICEID_ANY   = "+"
    IOT_EVENT_ANY      = "+"

    IOT_DEVICE_SENSOR_TYPE   = "DEMOSENSOR_T"
    IOT_DEVICE_SENSOR_ID     = "TEMPSENSOR_1"
    IOT_DEVICE_ACTUATOR_TYPE = "DEMOACTUATOR_T"
    IOT_DEVICE_ACTUATOR_ID   = "ITAG_ALARM_1"
    IOT_EVENT_READING        = "reading"
    IOT_EVENT_CURRENT_STATE  = "current_state"
    IOT_CMD_NEW_STATE        = "new_state"

    TEMPERATURE_THRESHOLD_1  = 40 
    TEMPERATURE_THRESHOLD_2  = 45 


    def __init__(self, iotApp):
        self.iotApp  = iotApp 
        self.eventMsgId  = None
        self.statusMsgId = None 
  

    def Start(self):
        self.iotApp.deviceEventCallback  = self.__EventHandler
        self.iotApp.deviceStatusCallback = self.__StatusHandler
        self.iotApp.subscriptionCallback = self.__SubscribeCallback

        self.eventMsgId  = self.iotApp.subscribeToDeviceEvents(self.IOT_DEVICETYPE_ANY, self.IOT_DEVICEID_ANY, self.IOT_EVENT_ANY) 
        self.statusMsgId = self.iotApp.subscribeToDeviceStatus(self.IOT_DEVICETYPE_ANY, self.IOT_DEVICEID_ANY)
        self.currentAlarmState = 0
  

    def __SubscribeCallback(self, msgId, qos):
        if msgId == self.statusMsgId:
            print("<< Subscription established for status messages at qos %s >> " % qos[0])
        elif msgId == self.eventMsgId:
            print("<< Subscription established for event messages at qos %s >> " % qos[0])
        
    def __EventHandler(self, event):
        print("%-33s%-30s%s" % (event.timestamp.isoformat(), event.device, event.event + ": " + json.dumps(event.data)))
        if event.deviceType == self.IOT_DEVICE_SENSOR_TYPE and event.deviceId == self.IOT_DEVICE_SENSOR_ID and event.event == self.IOT_EVENT_READING:
            temperature = event.data['temperature']
            self.__TemperatureEventHandler(temperature)
        
        if event.deviceType == self.IOT_DEVICE_ACTUATOR_TYPE and event.deviceId == self.IOT_DEVICE_ACTUATOR_ID and event.event == self.IOT_EVENT_CURRENT_STATE:
            alarm = event.data['alarm']
            print("Received alarm current state: ", alarm)
            self.currentAlarmState = alarm
 
        
    def __StatusHandler(self, status):
        if status.action == "Disconnect":
            summaryText = "%s %s (%s)" % (status.action, status.clientAddr, status.reason)
        else:
            summaryText = "%s %s" % (status.action, status.clientAddr)

    def __TemperatureEventHandler(self,temperature):
        print("Received temperature reading: ", temperature)
        desiredAlarmState = 0
        if temperature > self.TEMPERATURE_THRESHOLD_2:
            desiredAlarmState = 2
        elif temperature > self.TEMPERATURE_THRESHOLD_1:
            desiredAlarmState = 1
        else:
            desiredAlarmState = 0

        if self.currentAlarmState != desiredAlarmState:
            newStateData = {'alarm': desiredAlarmState }
            print("Publishing new alarm state: " , desiredAlarmState)
            self.iotApp.publishCommand(self.IOT_DEVICE_ACTUATOR_TYPE,self.IOT_DEVICE_ACTUATOR_ID,self.IOT_CMD_NEW_STATE,"json",newStateData)

 
 





def main():

    print('Starting demo control application...')

    # Initialize Dbus Main Loop
    mainloop = GObject.MainLoop()
    iotApp   = None


   # Connect to IBM Watson IOT Platform
    try:
            #   iotAppOptions = {"org"           : IOT_ORGANIZATION, 
            #                    "id"            : IOT_APPID,
            #                     "auth-method"  : IOT_AUTHMETHOD, 
            #                     "auth-key"     : IOT_AUTHKEY,
            #                     "auth-token"   : IOT_AUTHTOKEN}

            # use ./iot_demo_control_application.cfg for client connection parameters
            iotAppOptions = ibmiotf.application.ParseConfigFile('./iot_demo_control_application.cfg')
            iotApp        = ibmiotf.application.Client(iotAppOptions)
            iotApp.connect()
    except Exception as e:
            print("Caught exception connecting device: %s" % str(e))
            sys.exit()


    appImpl = SimpleControlApplicationImpl(iotApp)
    appImpl.Start()


    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()

    iotApp.disconnect()
    print('Exiting demo control application...')

if __name__ == '__main__':
    main()


