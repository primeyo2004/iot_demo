#!/usr/bin/env python3
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


import dbus
from xml.dom import minidom



BLUEZ_OBJECT_PATH          = '/org/bluez'
BLUEZ_SERVICE_NAME         = 'org.bluez'
BLUEZ_DEVICE_IFACE         = 'org.bluez.Device1'
GATT_SERVICE_IFACE         = 'org.bluez.GattService1'
GATT_CHRC_IFACE            = 'org.bluez.GattCharacteristic1'

DBUS_INTROSPECTABLE_IFACE  = 'org.freedesktop.DBus.Introspectable'
DBUS_PROP_IFACE            = 'org.freedesktop.DBus.Properties'

def get_bluez_childnodes(bus, path):
    # use dbus introspect approach which is more efficient
    # compare with org.freedesktop.DBus.ObjectManager.GetManagedObjects()
    # should the system has too many d-bus objects
    bluez_childnode_names = []
    intro = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, path), DBUS_INTROSPECTABLE_IFACE)
    intro_doc  = minidom.parseString(intro.Introspect())
    intro_node = intro_doc.documentElement
    intro_childnodes = intro_node.getElementsByTagName("node")
    for cn in intro_childnodes:
        bluez_childnode_names.append(cn.getAttribute('name'))
    return bluez_childnode_names 


class DBusClient:
    def __init__(self, bus, path, iface_name, proxyObject):
        self.Bus = bus
        self.Path = path
        self.IfaceName = iface_name
        self.ProxyObject = proxyObject

    def GetInterface(self):
        return dbus.Interface(self.ProxyObject, self.IfaceName)

    def GetProperty(self, propname):
        dbus_iface = self.GetInterface() 
        try:
            return dbus_iface.Get(self.IfaceName , propname, dbus_interface=DBUS_PROP_IFACE)
        except dbus.exceptions.DBusException as ex:
            # Ignore error if no property and return null 
            if ex.get_dbus_name() != 'org.freedesktop.DBus.Error.InvalidArgs':
                raise ex
            return None

    def LoadGattChildren(self):
        pass

class BluezClientCharacteristic(DBusClient):
    def __init__(self, bus, path, iface_name, proxyObject):
        DBusClient.__init__(self, bus, path, iface_name, proxyObject)

    def ReadValue(self, reply_handler=None, error_handler=None):
        iface = self.GetInterface()
        return iface.ReadValue({},
                reply_handler=reply_handler,
                error_handler=error_handler,
                dbus_interface=GATT_CHRC_IFACE)

    def WriteValue(self, value, reply_handler=None, error_handler=None):
        iface = self.GetInterface()
        return iface.WriteValue(value, {},
                 reply_handler=reply_handler,
                error_handler=error_handler,
                dbus_interface=GATT_CHRC_IFACE)
 
    @property
    def UUID(self):
        return self.GetProperty('UUID')

    @property
    def Service(self):
        return self.GetProperty('Service')

    @property
    def Value(self):
        return self.GetProperty('Value')

    @property
    def Notifying(self):
        return self.GetProperty('Notifying')

    @property
    def Flags(self):
        return self.GetProperty('Flags')

    @property
    def WriteAcquired(self):
        return self.GetProperty('WriteAcquired')

    @property
    def NotifyAcquired(self):
        return self.GetProperty('NotifyAcquired')


class BluezClientService(DBusClient):
    def __init__(self, bus, path, iface_name, proxyObject):
        DBusClient.__init__(self, bus, path, iface_name, proxyObject)
        self.__characteristics = None

    def LoadGattChildren(self):
        if self.__characteristics is None:
            self.__characteristics = {}
            global get_bluez_childnodes
            characteristics = get_bluez_childnodes(self.Bus, self.Path)
            for chrc in characteristics:
                chrc_path = self.Path + '/' + chrc
                chrc_proxy_object = self.Bus.get_object(BLUEZ_SERVICE_NAME, chrc_path)
                chrc_client = BluezClientCharacteristic(self.Bus, chrc_path, GATT_CHRC_IFACE, chrc_proxy_object)
                self.__characteristics[chrc_client.UUID] = chrc_client

    def GetCharactristic(self, uuid):
        self.LoadGattChildren()
        if uuid in self.__characteristics.keys():
            return self.__characteristics[uuid]
        return None

   
    def GetAllCharacteristics(self):
        self.LoadGattChildren()
        return self.__characteristics

    @property
    def UUID(self):
        return self.GetProperty('UUID')

    @property
    def Device(self):
        return self.GetProperty('Device')

    @property
    def Primary(self):
        return self.GetProperty('Primary')

    @property
    def Includes(self):
        return self.GetProperty('Includes')


class BluezClientDevice(DBusClient):
    def __init__(self, bus, path, iface_name, proxyObject):
        DBusClient.__init__(self, bus, path, iface_name, proxyObject)
        self.__services = None

    def LoadGattChildren(self):
        if self.__services is None:
            self.__services = {}
            global get_bluez_childnodes
            services = get_bluez_childnodes(self.Bus, self.Path)
            for serv in services:
                serv_path = self.Path + '/' + serv
                serv_proxy_object = self.Bus.get_object(BLUEZ_SERVICE_NAME, serv_path)
                serv_client = BluezClientService(self.Bus, serv_path, GATT_SERVICE_IFACE, serv_proxy_object)
                self.__services[serv_client.UUID] = serv_client 

    def GetService(self, uuid):
        self.LoadGattChildren()
        if uuid in self.__services.keys():
            return self.__services[uuid]
        return None

    def GetAllServices(self):
        self.LoadGattChildren()
        return self.__services

    def Connect(self, reply_handler=None,error_handler=None):
        dev_iface = self.GetInterface()
        dev_iface.Connect(reply_handler=reply_handler,
                          error_handler=error_handler)

    def Disconnect(self):
        dev_iface = self.GetInterface()
        dev_iface.Disconnect()

    @property
    def Address(self):
        return self.GetProperty('Address')

    @property
    def AddressType(self):
        return self.GetProperty('AddressType')

    @property
    def Name(self):
        return self.GetProperty('Name')

    @property
    def Alias(self):
        return self.GetProperty('Alias')

    @property
    def Class(self):
        return self.GetProperty('Class')

    @property
    def Appearance(self):
        return self.GetProperty('Appearance')

    @property
    def Icon(self):
        return self.GetProperty('Icon')

    @property
    def Paired(self):
        return self.GetProperty('Paired')

    @property
    def Trusted(self):
        return self.GetProperty('Trusted')

    @property
    def Blocked(self):
        return self.GetProperty('Blocked')

    @property
    def LegacyPairing(self):
        return self.GetProperty('LegacyPairing')

    @property
    def RSSI(self):
        return self.GetProperty('RSSI')

    @property
    def Connected(self):
        return self.GetProperty('Connected')

    @property
    def UUIDs(self):
        return self.GetProperty('UUIDs')

    @property
    def Modalias(self):
        return self.GetProperty('Modalias')

    @property
    def Adapter(self):
        return self.GetProperty('Adapter')

    @property
    def ManufacturerData(self):
        return self.GetProperty('ManufacturerData')

    @property
    def ServiceData(self):
        return self.GetProperty('ServiceData')

    @property
    def TxPower(self):
        return self.GetProperty('TxPower')

    @property
    def ServicesResolved(self):
        return self.GetProperty('ServicesResolved')

    @property
    def AdvertisingFlags(self):
        return self.GetProperty('AdvertisingFlags')

    @property
    def AdvertisingData(self):
        return self.GetProperty('AdvertisingData')


def FetchDevices(bus, device_filter_callback, adapter='hci0'):
    bluez_dev_clients = []
    adapter_path = BLUEZ_OBJECT_PATH + '/' + adapter
    devices = get_bluez_childnodes(bus, adapter_path)
    for dev in devices:
        dev_path = adapter_path + '/' + dev
        dev_proxy_object = bus.get_object(BLUEZ_SERVICE_NAME, dev_path)
        dev_client = BluezClientDevice(bus, dev_path, BLUEZ_DEVICE_IFACE, dev_proxy_object)

        if device_filter_callback(dev_client):
            bluez_dev_clients.append (dev_client)

    return bluez_dev_clients 


