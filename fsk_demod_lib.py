# fsk_demod_lib.py
'''
Demodulates signal using FSK
'''

import scipy.signal.signaltools as sigtool
import scipy.signal as signal 
import numpy as np
import matplotlib.pyplot as pyplot
import time

def crc_remainder(inbits, poly_bitstr):
    """
    Calculates the CRC remainder of arriving input bits
    """
    # get number of sent bits
    numbits = len(inbits) - len(poly_bitstr) + 1  # len(in) - len(pad)
    inbits = list(inbits)
    while '1' in inbits[:numbits]:
        cur_shift = inbits.index('1')
        for i in range(len(poly_bitstr)):
            if poly_bitstr[i] == inbits[cur_shift + i]:
                inbits[cur_shift + i] = '0'
            else: 
                inbits[cur_shift + i] = '1'

    return ''.join(inbits)[numbits:]

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


def hilbert(signal):
    """
    Wrapper for signal.hilbert() to optimize runtime
    """
    # Padding to optimize length
    padding = np.zeros(int(2**np.ceil(np.log2(len(signal)))) - len(signal))
    padding = np.zeros(int(2**np.ceil(np.log2(len(signal)))) - len(signal))
    
    tohilbert = np.hstack((signal, padding)) 
    
    # get envelope and cut padding
    result = sigtool.hilbert(tohilbert)
    result = result[0:len(signal)]
    
    return np.abs(result)

def demod(carrier, Fs, symbolrate, DATA_SAMPLES, CRC_SAMPLES, SAMP_PER_SYMBOL, bitspersym): # whole_sig, start):
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
    print "Applying envelope, len(carrier_diff): "+ str(len(carrier_diff))
    '''
    padding = np.zeros(int(2**np.ceil(np.log2(len(carrier_diff)))) - len(carrier_diff))
    tohilbert = np.hstack((carrier_diff, padding)) 
    result = signal.hilbert(tohilbert)
    result = result[0:len(carrier_diff)]
    carrier_env = np.abs(result)
    #carrier_env = np.abs(sigtool.hilbert(carrier_diff))
    '''
    carrier_env = hilbert(carrier_diff)

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
    carrier_filtered_new = carrier_filtered[i-DATA_SAMPLES-CRC_SAMPLES:i]  # get relevant data
    print "...done in {} seconds".format(time.time() - start_time)

    #pyplot.plot(carrier_filtered)
    #pyplot.plot([i, i-1], [60,0])
    #pyplot.plot([split1]*len(pre_carrier))
    #pyplot.plot([split2]*len(pre_carrier))
    #pyplot.plot([split3]*len(pre_carrier))
    #pyplot.show()

    start_time = time.time()
    print "Decoding data"
    rx_data = decode(carrier_filtered_new, Fs, symbolrate, bitspersym, SAMP_PER_SYMBOL)
    print "...done in {} seconds".format(time.time() - start_time)
    print "outbits: "+str(np.array(rx_data))

    data_str = ''.join(str(i) for i in rx_data)
    # Detect all zero false positive
    if data_str.lstrip('0') != '':
        # Detect errors if valid signal
        error_code = crc_remainder(data_str, '11011')
        print error_code
    else: 
        print 'Invalid Signal'
    
    # [:-4] cuts CRC error code out of data_str
    return data_str[:-4], error_code

