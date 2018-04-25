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

last_fft150 = last_fft350 = 1000000000

HIGH_FREQ = 400
LOW_FREQ  = 300
BAND = 25

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

        low_band = np.mean( np.abs(fft[LOW_FREQ-BAND : LOW_FREQ+BAND]) )
        high_band = np.mean( np.abs(fft[HIGH_FREQ-BAND : HIGH_FREQ+BAND]) )


        print "high: " + str(np.abs(fft[HIGH_FREQ])) + " high band: " + str(high_band)

        if np.abs(fft[HIGH_FREQ]) > 2*high_band:
            print "Detected"
        #last_fft150 = new_fft150
        #last_fft350 = new_fft350
    except KeyboardInterrupt:
        adc.stop_adc()
