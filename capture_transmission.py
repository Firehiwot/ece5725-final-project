#
# capture_transmission.py
# Angus Gibbs (aag233) and Joao Pedro Carvao (jc2697)
#

import time
from mcp3008 import read_adc
import numpy as np
import fsk_demod_lib

# Set up the ADC
SAMPLING_RATE = 7500
'''
GAIN = 1
CHANNEL = 0
adc = ADC_lib.ADS1115()
adc.start_adc(CHANNEL, gain=GAIN, data_rate=SAMPLING_RATE)
'''
# Define the transmission characteristics
M = 2  # number of bits per symbol
SYMBOL_RATE = 4
SAMP_PER_SYMBOL = SAMPLING_RATE / SYMBOL_RATE
HIGH_FREQ = 400
LOW_FREQ = 300
PEAK_BANDWIDTH = 5
AVG_BANDWIDTH = 30
PEAK_HEIGHT = 1.4

PREFIX_SAMPLES = 3*SAMPLING_RATE 
DATA_BITS = 16  # bits
DATA_SAMPLES = (DATA_BITS / M) * SAMP_PER_SYMBOL
TRANSMISSION_LENGTH = PREFIX_SAMPLES + DATA_SAMPLES + SAMP_PER_SYMBOL  # samples

# Keep a buffer of samples
start_buffer = [0] * SAMP_PER_SYMBOL
detected_buffer = [0] * TRANSMISSION_LENGTH

def sample_slot(arr, start_index=0):
    """
    Sample one time slot's worth of samples from the ADC.

    Arguments:
        arr (list): The array to put the samples in
        start_index (int, optional): The index at which to put the first
                                     sample
    """
    next_time = time.time()

    for i in range(SAMP_PER_SYMBOL):
        next_time = next_time + 1 / float(SAMPLING_RATE)

        while time.time() < next_time:
            pass

        arr[i+start_index] = read_adc(0)

def start_recording():
    """
    Buffer an entire transmission after the start of transmission is detected.
    """
    for samp in range(TRANSMISSION_LENGTH/SAMP_PER_SYMBOL):
        sample_slot(detected_buffer, (samp)*SAMP_PER_SYMBOL)

def parse_recording():
    """
    Find the end of the prefix and then pass the data samples to the decoder.
    """
    fsk_demod_lib.demod(detected_buffer, SAMPLING_RATE, SYMBOL_RATE, DATA_SAMPLES, SAMP_PER_SYMBOL, M)

# Continuously look for a start of transmission
while True:
    try:
        # Sample one slot's worth of samples from the ADC
        sample_slot(start_buffer)

        # Check if there has been a spike at the high and low frequencies,
        # indicating the start of a transmission
        fft = np.fft.fft(start_buffer)
        low_band_avg = np.mean(np.abs(fft[SYMBOL_RATE*LOW_FREQ-AVG_BANDWIDTH:
                                          SYMBOL_RATE*LOW_FREQ+AVG_BANDWIDTH]))
        high_band_avg = np.mean(np.abs(fft[SYMBOL_RATE*HIGH_FREQ-AVG_BANDWIDTH:
                                           SYMBOL_RATE*HIGH_FREQ+AVG_BANDWIDTH]))
        low_band_peak = np.mean(np.abs(fft[SYMBOL_RATE*LOW_FREQ-PEAK_BANDWIDTH:
                                           SYMBOL_RATE*LOW_FREQ+PEAK_BANDWIDTH]))
        high_band_peak = np.mean(np.abs(fft[SYMBOL_RATE*HIGH_FREQ-PEAK_BANDWIDTH:
                                            SYMBOL_RATE*HIGH_FREQ+PEAK_BANDWIDTH]))
        #print "high: {}\thigh band: {}".format(high_band_peak, high_band_avg)  
        #print "low: {}\tlow band: {}".format(low_band_peak, low_band_avg)
        if (high_band_peak > PEAK_HEIGHT*high_band_avg and
            low_band_peak > PEAK_HEIGHT*low_band_avg):
            print "Detected"
            start_recording()
            print "Finished recording"
            parse_recording()
    except KeyboardInterrupt:
        GPIO.cleanup()

GPIO.cleanup()

