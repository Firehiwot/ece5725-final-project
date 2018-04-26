# fsk_demod_lib.py
'''
Demodulates signal using FSK
'''

import scipy.signal.signaltools as sigtool
import scipy.signal as signal 
import numpy as np
import matplotlib.pyplot as pyplot

def demod(carrier, Fs, bitrate):
    """
    Demodulates the carrier into a bit string.
    """
    # differentiate received carrier signal
    carrier_diff = np.diff(carrier, 1)

    # detect envelope to extract digital data 
    carrier_env = np.abs(sigtool.hilbert(carrier_diff))

    # create low pass filter
    lpf = signal.firwin(numtaps=100, cutoff=bitrate*2, nyq=Fs/2)

    # filter our signal 
    carrier_filtered = signal.lfilter( lpf, 1.0, carrier_env)

    pyplot.plot(carrier)
    pyplot.plot(carrier_filtered)
    pyplot.show()

    # slicing
    mean = np.mean(carrier_filtered)

    # slice to ones and zeros to extract original bits
    rx_data = []
    sampled_signal = carrier_filtered[int(Fs/bitrate/2) : len(carrier_filtered) : int(Fs/bitrate)]
    for bit in sampled_signal: 
        if bit > mean: 
            rx_data.append(1)
        else: 
            rx_data.append(0)

    print "outbits: "+str(np.array(rx_data))

    bits = [1, 0, 1, 0]
    biterror = 0
    for i, bit in enumerate(bits):
        if bit != rx_data[i]:
            biterror += 1

    print biterror
