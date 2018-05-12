#
# test_mcp3008.py
# Angus Gibbs (aag233) and Joao Pedro Carvao (jc2697)
#
# Script to test the MCP3008 library in mcp3008.py
#

import time
import RPi.GPIO as GPIO
import matplotlib.pyplot as pyplot
import numpy as np

from mcp3008 import read_adc

# Set the sampling rate
Fs = 7500

# Read in one second of samples
samples = []
next_time = time.time() + 1 / float(Fs)
for i in range(Fs):
  while time.time() < next_time:
    continue

  samples.append(read_adc(0))

  next_time += 1 / float(Fs)

# Calculate and plot an FFT of the received samples
fft = np.log(np.abs(np.fft.fft(samples)))
pyplot.plot(np.fft.fftfreq(Fs, 1/float(Fs)), fft)
pyplot.show()

# Clean up GPIO inputs
GPIO.cleanup()
