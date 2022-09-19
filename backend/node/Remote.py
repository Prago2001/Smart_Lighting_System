from digi.xbee.devices import RemoteZigBeeDevice
from digi.xbee.io import IOLine,IOValue,IOMode


main_line = IOLine.DIO4_AD4
line_1 = IOLine.DIO12
line_2 = IOLine.DIO11_PWM1
line_3 = IOLine.DIO8
dim_lines = [line_1,line_2,line_3]
temperature = IOLine.DIO0_AD0
current = IOLine.DIO1_AD1
on = IOValue.HIGH
off = IOValue.LOW

class Remote(RemoteZigBeeDevice):
    def __init__(self,node:RemoteZigBeeDevice):
        self.remote_device = node
        self.remote_device.set_io_configuration(temperature,IOMode.ADC)
        self.remote_device.set_io_configuration(current,IOMode.ADC)
        self.remote_device.set_io_configuration(main_line,IOMode.DIGITAL_OUT_LOW)
        for line in dim_lines:
            self.remote_device.set_io_configuration(line,IOMode.DIGITAL_OUT_LOW)
        self._64bit_addr = str(self.remote_device.get_64bit_addr())
