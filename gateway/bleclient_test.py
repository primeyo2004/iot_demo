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
import dbus
import sys
from dbus.mainloop.glib import DBusGMainLoop

try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject


def my_cb (dev):
    if dev.Name == 'ITAG':
        if dev.Connected:
            return True
    return False

class SampleAsyncHandler:
    def __init__(self,chrc):
        self.__chrc = chrc

    def sample_connect_cb(self):
        print('Connected.')

    def sample_generic_error_cb2(self,error):
        print('D-Bus call failed2: ' + str(error))
        self.__chrc.Connect(reply_handler=self.sample_connect_cb,error_handler=self.sample_generic_error_cb2)

    def sample_generic_error_cb(self,error):
        print('D-Bus call failed: ' + str(error))

    def sample_read_chrc_cb(self,value):
        print('sample_read_chrc_cb:', int(value[0]))
        if int(value[0]) == 0:
            self.__chrc.WriteValue([0x01],reply_handler=self.sample_write_chrc_cb,error_handler=self.sample_generic_error_cb)
        if int(value[0]) == 1:
            self.__chrc.WriteValue([0x02],reply_handler=self.sample_write_chrc_cb,error_handler=self.sample_generic_error_cb)
        if int(value[0]) == 2:
            self.__chrc.WriteValue([0x00],reply_handler=self.sample_write_chrc_cb,error_handler=self.sample_generic_error_cb)


    def sample_write_chrc_cb(self):
        print('sample_write_chrc_cb:')
        self.__chrc.ReadValue(reply_handler=self.sample_read_chrc_cb, error_handler=self.sample_generic_error_cb)


def tmp(dev):
    return True

def main():

    DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    global mainloop
    mainloop = GObject.MainLoop()

    bluezdevs = bleclient.FetchDevices(bus, tmp)
    if len(bluezdevs) == 0:
        print ('No connected device found.')

    for bd  in bluezdevs:
        print('----------')
        print(bd.Path)
        print(bd.IfaceName)
        print(bd.Address)
        print(bd.AddressType)
        print(bd.Name)
        print(bd.Alias)
        print(bd.Class)
        print(bd.Appearance)
        print(bd.Icon)
        print(bd.Paired)
        print(bd.Trusted)
        print(bd.Blocked)
        print(bd.LegacyPairing)
        print(bd.RSSI)
        print(bd.Connected)
        print(bd.UUIDs[0])
        print(bd.Modalias)
        print(bd.Adapter)
        print(bd.ManufacturerData)
        print(bd.ServiceData)
        print(bd.TxPower)
        print(bd.ServicesResolved)
        print(bd.AdvertisingFlags)
        print(bd.AdvertisingData)
        print('----------')
        for s in bd.GetAllServices().values():
            print('----------')
            print(s.Path)
            print(s.IfaceName)
            print(s.UUID)
            print(s.Device)
            print(s.Primary)
            print(s.Includes)
            print('----------')
            for c in s.GetAllCharacteristics().values():
                print('----------')
                print(c.Path)
                print(c.IfaceName)
                print(c.UUID)
                print(c.Service)
                print(c.Value)
                print(c.Notifying)
                print(c.Flags)
                print(c.WriteAcquired)
                print(c.NotifyAcquired)
                print('----------')

        global cchar

        cs = bd.GetService('00001802-0000-1000-8000-00805f9b34fb') 
        cchar = cs.GetCharactristic('00002a06-0000-1000-8000-00805f9b34fb')
        print(cchar.Path)
        print(cchar.Notifying)
        handler = SampleAsyncHandler(cchar)

        cchar.ReadValue(reply_handler=handler.sample_read_chrc_cb,error_handler=handler.sample_generic_error_cb)
#       cchar.WriteValue([0x01],reply_handler=handler.sample_write_chrc_cb,error_handler=handler.sample_generic_error_cb)
#       print('Read:', int( cchar.ReadValue(reply_handler=handler.sample_read_chrc_cb,error_handler=handler.sample_generic_error_cb)[0]))
#       cchar.ReadValue(reply_handler=handler.sample_read_chrc_cb,error_handler=handler.sample_generic_error_cb)
#       cchar.WriteValue([0x02],reply_handler=handler.sample_write_chrc_cb,error_handler=handler.sample_generic_error_cb)
#       cchar.ReadValue(reply_handler=handler.sample_read_chrc_cb,error_handler=handler.sample_generic_error_cb)
#       print('Read:', int( cchar.ReadValue(reply_handler=handler.sample_read_chrc_cb,error_handler=handler.sample_generic_error_cb)[0]))
#       cchar.WriteValue([0x00],reply_handler=handler.sample_write_chrc_cb,error_handler=handler.sample_generic_error_cb)
#       cchar.ReadValue(reply_handler=handler.sample_read_chrc_cb,error_handler=handler.sample_generic_error_cb)
#       print('Read:', int( cchar.ReadValue(reply_handler=handler.sample_read_chrc_cb,error_handler=handler.sample_generic_error_cb)[0]))


    try:
        mainloop.run()
    except KeyboardInterrupt:
        mainloop.quit()


if __name__ == '__main__':
    main()


