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

import tc74


def main():
    sensor = tc74.create_TC74Sensor('TC74SensorDummy',1,0x4a)
    print (sensor.read())

if __name__ == '__main__':
    main()
