# fsk_demod_lib.py
'''
Demodulates signal using FSK
'''

import scipy.signal.signaltools as sigtool
import scipy.signal as signal 
import numpy as np
import matplotlib.pyplot as pyplot
import time

def decode(signal, Fs, symbolrate, bitspersym, SAMP_PER_SYMBOL):
    # Find the splits
    splits = []
    num_splits = 2 ** bitspersym - 1
    for i_sym in range(num_splits):
        symbols = signal[i_sym*SAMP_PER_SYMBOL:(i_sym+2)*SAMP_PER_SYMBOL]
        splits.append(np.mean(symbols))

    # Decode bits using splits
    sampled_signal = signal[int(Fs/symbolrate/2):len(signal):int(Fs/symbolrate)]
    outbits = []
    for sample in sampled_signal:
        # Find the highest split under which the sample fits
        split = 0
        while split < num_splits and sample > splits[split]:
            split += 1

        # Decode the bits from the split
        outbits += list(format(split, '0' + str(bitspersym) + 'b'))

    """
    pyplot.plot(signal)
    for split in splits:
        pyplot.plot([split] * len(signal))
    pyplot.show()
    """

    return [int(bit) for bit in outbits]

def demod(carrier, Fs, symbolrate, DATA_SAMPLES, SAMP_PER_SYMBOL, bitspersym): # whole_sig, start):
    """
    Demodulates the carrier into a bit string.
    """
    # differentiate received carrier signal
    start_time = time.time()
    print "Differentiating"
    carrier_diff = np.diff(carrier, 1)
    print "...done in {} seconds".format(time.time() - start_time)

    # detect envelope to extract digital data 
    start_time = time.time()
    print "Applying envelope"
    carrier_env = np.abs(sigtool.hilbert(carrier_diff))
    print "...done in {} seconds".format(time.time() - start_time)

    # create low pass filter
    lpf = signal.firwin(numtaps=100, cutoff=symbolrate*2, nyq=Fs/2)

    # filter our signal 
    start_time = time.time()
    print "Applying LPF"
    carrier_filtered = signal.lfilter( lpf, 1.0, carrier_env)
    print "...done in {} seconds".format(time.time() - start_time)
    
    # detect start of data
    start_time = time.time()
    print "Detecting start of data"
    M = 150  # window size
    i = len(carrier_filtered) - M - 1
    thresh = 2
    old_avg = np.inf
    new_avg = np.mean(carrier_filtered[i:i+M])
    while new_avg < thresh*old_avg:
        old_avg = new_avg
        i -= M
        new_avg = np.mean(carrier_filtered[i:i+M])
    carrier_filtered = carrier_filtered[i-DATA_SAMPLES:i]  # get relevant data
    print "...done in {} seconds".format(time.time() - start_time)
    """
    i = 7000
    thresh = 0.88
    new_avg = pre_mean
    while new_avg > pre_mean*thresh:
        new_avg = np.mean(carrier_filtered[i:i+M])
        i += M
    carrier_filtered = carrier_filtered[i-M:i-M+DATA_SAMPLES]
    """
    
    """
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
    """

    #pyplot.plot(pre_carrier)
    #pyplot.plot([i, i-1], [60,0])
    #pyplot.plot([split1]*len(pre_carrier))
    #pyplot.plot([split2]*len(pre_carrier))
    #pyplot.plot([split3]*len(pre_carrier))
    #pyplot.show()

    start_time = time.time()
    print "Decoding data"
    rx_data = decode(carrier_filtered, Fs, symbolrate, bitspersym, SAMP_PER_SYMBOL)
    print "...done in {} seconds".format(time.time() - start_time)
    print "outbits: "+str(np.array(rx_data))

    """
    bits = [1, 0, 1, 0]
    biterror = 0
    for i, bit in enumerate(bits):
        if bit != rx_data[i]:
            biterror += 1

    print biterror
    """
