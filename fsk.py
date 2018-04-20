# fsk.py

import time
import numpy as np
import Adafruit_ADS1x15 as ADC_lib
from matplotlib import pyplot

if __name__ == "__main__":
    # Read from ADC channel 0
    CHANNEL = 0

    # Choose ADC gain (see ADC sample file for description)
    GAIN = 1

    # Initialize ADC
    adc = ADC_lib.ADS1115()
    adc.start_adc(CHANNEL, gain=GAIN, data_rate=860)

    # Read in 1024 values from the ADC, one value every 1/fs seconds
    # where fs = the sampling frequency = 860 samples per second
    n_samp = 1024
    fs = 860.0
    adc_vals = [0] * n_samp
    start_time = time.time()
    next_time = time.time() + 1/fs
    for i in range(n_samp):
        while time.time() < next_time:
            pass
        next_time += 1/fs
        adc_vals[i] = adc.get_last_result()
    end_time = time.time()
    print("Time per sample: {}".format((end_time - start_time) / 1024.0))

    # Calculate the FFT of the captured ADC values
    fft_out = np.fft.fft(adc_vals)
    fft_freqs = np.fft.fftfreq(fft_out.size, d=(1/860.0))

    # Plot the input and the FFT
    pyplot.subplot(2, 1, 1)
    pyplot.plot(fft_freqs, np.log(np.abs(fft_out)))
    pyplot.subplot(2, 1, 2)
    pyplot.plot(adc_vals)

    # Show the plot
    pyplot.show()

    # Stop the ADC
    adc.stop_adc()
