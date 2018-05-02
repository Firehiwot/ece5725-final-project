import time
import RPi.GPIO as GPIO
import matplotlib.pyplot as pyplot
import numpy as np

from mcp3008 import read_adc

Fs = 44100

samples = []
next_time = time.time() + 1 / float(Fs)
for i in range(Fs):
    while time.time() < next_time:
        continue

    samples.append(read_adc(0))

    next_time += 1 / float(Fs)

fft = np.log(np.abs(np.fft.fft(samples)))

#pyplot.plot(np.fft.fftfreq(Fs, 1/float(Fs)), fft)
#pyplot.show()

GPIO.cleanup()
