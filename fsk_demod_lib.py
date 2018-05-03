# fsk_demod_lib.py
'''
Demodulates signal using FSK
'''

import scipy.signal.signaltools as sigtool
import scipy.signal as signal 
import numpy as np
import matplotlib.pyplot as pyplot

#def decode(carrier_filtered, bitspersym):


def demod(carrier, Fs, symbolrate, DATA_SAMPLES, SAMP_PER_SYMBOL, bitspersym): # whole_sig, start):
    """
    Demodulates the carrier into a bit string.
    """
    # differentiate received carrier signal
    carrier_diff = np.diff(carrier, 1)

    # detect envelope to extract digital data 
    carrier_env = np.abs(sigtool.hilbert(carrier_diff))

    # create low pass filter
    lpf = signal.firwin(numtaps=100, cutoff=symbolrate*2, nyq=Fs/2)

    # filter our signal 
    carrier_filtered = signal.lfilter( lpf, 1.0, carrier_env)
    
    # slicing
    pre_mean = np.mean(carrier_filtered[1000:5000])
    pre_carrier = carrier_filtered 
    # detect start of data
    M = 150  # window size
    i = 7000
    thresh = 0.98
    new_avg = pre_mean
    while new_avg > pre_mean*thresh:
        new_avg = np.mean(carrier_filtered[i : i+M])
        i += M
    
    carrier_filtered = carrier_filtered[i-M + 0*SAMP_PER_SYMBOL : i-M+DATA_SAMPLES]  # get relevant data
    
    # split signal into four regions
    mean = np.mean(carrier_filtered)
    mean = np.mean(carrier_filtered[carrier_filtered < 2*mean])
    
    carrier_prefix = carrier_filtered[0:4*SAMP_PER_SYMBOL]

    # determine "decision regions"
    split2 = np.mean(carrier_prefix)
    split1 = np.mean(carrier_prefix[carrier_prefix < split2])  
    split3 = np.mean(carrier_prefix[carrier_prefix > split2])
    
    # slice to ones and zeros to extract original bits
    rx_data = []
    sampled_signal = carrier_filtered[int(Fs/symbolrate/2) : len(carrier_filtered) : int(Fs/symbolrate)]
    #rx_data = decode(carrier_filtered, bitspersym)

    for bit in sampled_signal: 
        if bit < split1: 
            rx_data.append(0)
            rx_data.append(0)
        elif bit < split2:
            rx_data.append(0)
            rx_data.append(1)
        elif bit < split3: 
            rx_data.append(1)
            rx_data.append(0)
        else: 
            rx_data.append(1)
            rx_data.append(1)

    #print "outbits: "+str(np.array(rx_data))

    pyplot.plot(pre_carrier)
    pyplot.plot([i, i-1], [60,0])
    pyplot.plot([split1]*len(pre_carrier))
    pyplot.plot([split2]*len(pre_carrier))
    pyplot.plot([split3]*len(pre_carrier))
    pyplot.show()

    print "outbits: "+str(np.array(rx_data))

    """
    bits = [1, 0, 1, 0]
    biterror = 0
    for i, bit in enumerate(bits):
        if bit != rx_data[i]:
            biterror += 1

    print biterror
    """
