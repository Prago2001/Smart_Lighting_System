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

        # self.remote_device.set_io_configuration(temperature,IOMode.ADC)
        # self.remote_device.set_io_configuration(current,IOMode.ADC)
        # self.remote_device.set_io_configuration(main_line,IOMode.DIGITAL_OUT_LOW)
        # for line in dim_lines:
        #     self.remote_device.set_io_configuration(line,IOMode.DIGITAL_OUT_LOW)

        self._64bit_addr = str(self.remote_device.get_64bit_addr())
        self.node_name = self.remote_device.get_node_id()
        
    
    def __str__(self):
        return self._64bit_addr

    def get_mains_value(self):
        if self.remote_device.get_dio_value(main_line) is on:
            return True
        else:
            return False
    
    def set_mains_value(self,switch_on : bool):
        if switch_on is True:
            self.remote_device.set_dio_value(main_line,on)
        else:
            self.remote_device.set_dio_value(main_line,off)
    

    def get_dim_value(self):
        if self.remote_device.get_dio_value(line_1) == on and self.remote_device.get_dio_value(line_2) == off and self.remote_device.get_dio_value(line_3) == off:
            return 25
        elif self.remote_device.get_dio_value(line_1) == on and self.remote_device.get_dio_value(line_2) == on and self.remote_device.get_dio_value(line_3) == off:
            return 50
        elif self.remote_device.get_dio_value(line_1) == on and self.remote_device.get_dio_value(line_2) == off and self.remote_device.get_dio_value(line_3) == on:
            return 75
        elif self.remote_device.get_dio_value(line_1) == on and self.remote_device.get_dio_value(line_2) == on and self.remote_device.get_dio_value(line_3) == on:
            return 100
        else:
            return 0
    
    def get_current_value(self):
        return round(self.remote_device.get_adc_value(current),2)
    
    def get_temperature_value(self):
        # t_val stands for actual temperature
        t_val = self.remote_device.get_adc_value(temperature)
        t_val = ((t_val * 1.2 / 1023) - 0.5) * 100
        return round(t_val,2)
    
    def set_dim_25(self):
        self.remote_device.set_dio_value(line_1,on)
        self.remote_device.set_dio_value(line_2,off)
        self.remote_device.set_dio_value(line_3,off)
    
    def set_dim_50(self):
        self.remote_device.set_dio_value(line_1,on)
        self.remote_device.set_dio_value(line_2,on)
        self.remote_device.set_dio_value(line_3,off)
    
    def set_dim_75(self):
        self.remote_device.set_dio_value(line_1,on)
        self.remote_device.set_dio_value(line_2,off)
        self.remote_device.set_dio_value(line_3,on)
    
    def set_dim_100(self):
        self.remote_device.set_dio_value(line_1,on)
        self.remote_device.set_dio_value(line_2,on)
        self.remote_device.set_dio_value(line_3,on)
    

    def set_dim_value(self,value:int):
        if value == 25:
            self.set_dim_25()
        elif value == 50:
            self.set_dim_50()
        elif value == 75:
            self.set_dim_75()
        elif value == 100:
            self.set_dim_100()
    
    def set_node_id(self, node_id):
        self.remote_device.set_node_id(node_id)
    