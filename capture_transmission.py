#
# capture_transmission.py
# Angus Gibbs (aag233) and Joao Pedro Carvao (jc2697)
#

import time
import Adafruit_ADS1x15 as ADC_lib
import numpy as np
import fsk_demod_lib

# Set up the ADC
SAMPLING_RATE = 860
GAIN = 1
CHANNEL = 0
adc = ADC_lib.ADS1115()
adc.start_adc(CHANNEL, gain=GAIN, data_rate=SAMPLING_RATE)

# Define the transmission characteristics
BIT_RATE = 1
SAMP_PER_BIT = SAMPLING_RATE / BIT_RATE
HIGH_FREQ = 400
LOW_FREQ = 300
PEAK_BANDWIDTH = 5
AVG_BANDWIDTH = 30
PEAK_HEIGHT = 1.4

PREFIX_LEN = 3
DATA_LEN = 4
TRANSMISSION_LENGTH = (PREFIX_LEN + DATA_LEN) * SAMP_PER_BIT

# Keep a buffer of samples
start_buffer = [0] * SAMP_PER_BIT
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

    for i in range(SAMP_PER_BIT):
        next_time = next_time + 1 / float(SAMP_PER_BIT)

        while time.time() < next_time:
            pass

        arr[i+start_index] = adc.get_last_result()

def start_recording():
    """
    Buffer an entire transmission after the start of transmission is detected.
    """
    detected_buffer[0:SAMP_PER_BIT] = start_buffer
    for samp in range(PREFIX_LEN + DATA_LEN - 1):
        sample_slot(detected_buffer, (samp+1)*SAMP_PER_BIT)

def parse_recording():
    """
    Find the end of the prefix and then pass the data samples to the decoder.
    """
    # Slide a window by 1/10 of the slot size until there is no longer a peak
    # detected at both the high and low frequencies for 3 consecutive shifts
    window_start = 0
    missing_peaks = 0
    while (missing_peaks < 3 and
           window_start + SAMP_PER_BIT <= len(detected_buffer)):
        # Check for peaks
        fft = np.fft.fft(detected_buffer[window_start:
                                         window_start+SAMP_PER_BIT])
        low_band_avg = np.mean(np.abs(fft[LOW_FREQ-AVG_BANDWIDTH:
                                          LOW_FREQ+AVG_BANDWIDTH]))
        high_band_avg = np.mean(np.abs(fft[HIGH_FREQ-AVG_BANDWIDTH:
                                           HIGH_FREQ+AVG_BANDWIDTH]))
        low_band_peak = np.mean(np.abs(fft[LOW_FREQ-PEAK_BANDWIDTH:
                                           LOW_FREQ+PEAK_BANDWIDTH]))
        high_band_peak = np.mean(np.abs(fft[HIGH_FREQ-PEAK_BANDWIDTH:
                                            HIGH_FREQ+PEAK_BANDWIDTH]))
        if (high_band_peak > PEAK_HEIGHT*high_band_avg and
            low_band_peak > PEAK_HEIGHT*low_band_avg):
            missing_peaks = 0
        else:
            missing_peaks += 1

        # Move the window
        window_start += int(SAMP_PER_BIT / 10)

    # Check if the end of the prefix could be determined
    if missing_peaks == 3:
        window_start -= int(SAMP_PER_BIT/10)
        print "Found start at {}".format(window_start)
        fsk_demod_lib.demod(detected_buffer[window_start:],
                            SAMPLING_RATE, BIT_RATE)
    else:
        print "Could not find start"

# Continuously look for a start of transmission
while True:
    # Sample one slot's worth of samples from the ADC
    sample_slot(start_buffer)

    # Check if there has been a spike at the high and low frequencies,
    # indicating the start of a transmission
    fft = np.fft.fft(start_buffer)
    low_band_avg = np.mean(np.abs(fft[LOW_FREQ-AVG_BANDWIDTH:
                                      LOW_FREQ+AVG_BANDWIDTH]))
    high_band_avg = np.mean(np.abs(fft[HIGH_FREQ-AVG_BANDWIDTH:
                                       HIGH_FREQ+AVG_BANDWIDTH]))
    low_band_peak = np.mean(np.abs(fft[LOW_FREQ-PEAK_BANDWIDTH:
                                       LOW_FREQ+PEAK_BANDWIDTH]))
    high_band_peak = np.mean(np.abs(fft[HIGH_FREQ-PEAK_BANDWIDTH:
                                        HIGH_FREQ+PEAK_BANDWIDTH]))
    #print "high: {}\thigh band: {}".format(high_band_peak, high_band_avg)
    #print "low: {}\tlow band: {}".format(low_band_peak, low_band_avg)
    if (high_band_peak > PEAK_HEIGHT*high_band_avg and
        low_band_peak > PEAK_HEIGHT*low_band_avg):
        print "Detected"
        start_recording()
        print "Finished recording"
        parse_recording()
