# ads1115_test.py
# Joao Pedro Carvao and Angus Gibbs
"""
Test ADS1115 ADC connected via I2C
"""

import Adafruit_ADS1x15 as ADC_lib
import time

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.

if __name__ == "__main__":
    # ADC Gain (see values above) and Channel (A0, A1, A2 -- see wiring)
    GAIN = 1
    CHANNEL = 0 
    # Create ADC Object
    adc = ADC_lib.ADS1115()
    # Start ADC
    adc.start(CHANNEL, gain=GAIN)
    while True:
        try:
            time.sleep(0.1)
            # Display ADC reading
            print "ADC Channel" + str(CHANNEL) + ": " +  str(adc.get_last_result())
        except KeyboardInterrupt:
            adc.stop_adc()
    
    adc.stop_adc()

