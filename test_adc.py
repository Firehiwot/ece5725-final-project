# test_adc.py
# Joao Pedro Carvao and Angus Gibbs
# ECE 5725 - Spring 2018

"""
Read value from ADC using software SPI
"""

import time
import RPi.GPIO as GPIO
import RPI_ADC0832 as SPI_ADC

# BCM RPi GPIO Numbering
MOSI = 10
MISO = 9
SCLK = 11

ADC_CHANNEL = 0

def adc_init(MOSI, MISO, SCLK):
    '''
    Returns initiated ADC object and updates pins
    '''
    # create ADC object
    adc = SPI_ADC.ADC0832()
    # update pins to accomodate wiring
    adc.clkPin = SCLK
    adc.doPin  = MISO
    adc.diPin  = MOSI
    # due to library "bug", SCLK must be reconfigured
    GPIO.setup(adc.clkPin, GPIO.OUT, initial=GPIO.HIGH)

    return adc


if __name__ == "__main__":
    # init ADC
    adc = adc_init(MOSI, MISO, SCLK)
    # read from ADC
    while True:
        try:
            valChannel = adc.read_adc(ADC_CHANNEL)
            print "ADC Channel" + str(ADC_CHANNEL) + " : " + str(valChannel)
        except KeyboardInterrupt: 
            adc.cleanup()

    adc.cleanup()
