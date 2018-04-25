import time
import Adafruit_ADS1x15 as ADC_lib
import numpy as np
import matplotlib.pyplot as plot

Fs = 860
bitrate = 1
samp_per_bit = Fs / bitrate

GAIN = 1
CHANNEL = 0

adc = ADC_lib.ADS1115()
adc.start_adc(CHANNEL, gain=GAIN, data_rate=860)

samps = [0] * samp_per_bit

last_fft = 1000000000

while True:
    try:
        next_time = time.time()

        for i in range(samp_per_bit):
            next_time = next_time + 1 / float(samp_per_bit)

            while time.time() < next_time:
                pass

            samps[i] = adc.get_last_result()

        fft = np.fft.fft(samps)

        #print np.abs(fft[150])
        #plot.plot(np.log(np.abs(fft)))
        #plot.show()

        print np.abs(fft[300])
        new_fft = np.abs(fft[300])
        if new_fft / last_fft > 5:
            print "Detected"
        last_fft = new_fft
    except KeyboardInterrupt:
        adc.stop_adc()
