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

import smbus

class TC74Sensor:
    def __init__(self, i2cbus, i2caddr):
        self.i2cbus  = i2cbus
        self.i2caddr = i2caddr

    def read(self):
        return 0 

class __TC74SensorDummy(TC74Sensor):
    def __init__(self, i2cbus, i2caddr):
        TC74Sensor.__init__(self,i2cbus,i2caddr)
        self.value = 0

    def read(self):
        if self.value > 100:
            self.value = 0
        self.value = self.value + 1
        return self.value 

class __TC74SensorImpl(TC74Sensor):
    def __init__(self, i2cbus, i2caddr):
        TC74Sensor.__init__(self,i2cbus,i2caddr)
        self.bus = smbus.SMBus(self.i2cbus)
        self.bus.write_byte(self.i2caddr,0x00)

    def read(self):
        return self.bus.read_byte(self.i2caddr)

def create_TC74Sensor(name,i2cbus,i2caddr):
    if name == 'TC74SensorImpl':
        return __TC74SensorImpl(i2cbus,i2caddr)
    elif name == 'TC74SensorDummy':
        return __TC74SensorDummy(i2cbus,i2caddr)

