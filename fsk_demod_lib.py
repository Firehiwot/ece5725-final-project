#
# fsk_demod_lib.py
# Angus Gibbs (aag233) and Joao Pedro Carvao (jc2697)
#
# Demodulates an MFSK signal into bits.
#

import time

import scipy.signal.signaltools as sigtool
import scipy.signal as signal 
import numpy as np
import matplotlib.pyplot as pyplot

def crc_remainder(inbits, poly_bitstr):
  """
  Calculates the CRC remainder of arriving input bits.

  Arguments:
    inbits (str): The input bitstring (with the remainder bits appended)
    poly_bitstr (str): The CRC polynomial
  """
  # Get number of sent bits
  numbits = len(inbits) - len(poly_bitstr) + 1  # len(in) - len(pad)
  inbits = list(inbits)

  # Divide and take the remainder until the CRC is left
  while '1' in inbits[:numbits]:
    cur_shift = inbits.index('1')
    for i in range(len(poly_bitstr)):
      if poly_bitstr[i] == inbits[cur_shift + i]:
        inbits[cur_shift + i] = '0'
      else: 
        inbits[cur_shift + i] = '1'

  return ''.join(inbits)[numbits:]

def decode(signal, Fs, symbolrate, bitspersym, SAMP_PER_SYMBOL):
  """
  Decode the received signal into bits.

  Arguments:
    signal (list of int): The received signal, truncated to start at the exact
                          prefix frame start
    Fs (int): The sampling rate
    symbolrate (int): The number of symbols per second
    bitspersym (int): The number of bits contained in one symbol
    SAMP_PER_SYMBOL (int): The number of samples sent for each symbol

  Returns:
    list of int
  """
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

  # Return the bits
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

def demod(carrier, Fs, symbolrate, DATA_SAMPLES, CRC_SAMPLES, SAMP_PER_SYMBOL, bitspersym):
  """
  Demodulates the carrier into a bit string.

  Arguments:
    carrier (list of int): The entire recorded transmission
    Fs (int): The sampling frequency
    symbolrate (int): The number of symbols per second
    DATA_SAMPLES (int): The number of prefix and data samples in the transmission
    CRC_SAMPLES (int): The number of CRC samples in the transmission
    SAMP_PER_SYMBOL (int): The number of samples needed to encode a symbol
    bitspersym (int): The number of bits per symbol

  Returns:
    list of int
  """
  # Differentiate received carrier signal
  carrier_diff = np.diff(carrier, 1)

  # Detect envelope to extract digital data 
  carrier_env = hilbert(carrier_diff)

  # Low pass filter the signal
  lpf = signal.firwin(numtaps=100, cutoff=symbolrate*2, nyq=Fs/2)
  carrier_filtered = signal.lfilter( lpf, 1.0, carrier_env)
  
  # Detect start of data using a sliding window averager
  M = 150  # window size
  i = len(carrier_filtered) - M - 1
  thresh = 2
  old_avg = np.inf
  new_avg = np.mean(carrier_filtered[i:i+M])
  while new_avg < thresh*old_avg:
    old_avg = new_avg
    i -= M
    new_avg = np.mean(carrier_filtered[i:i+M])
  carrier_filtered_new = carrier_filtered[i-DATA_SAMPLES-CRC_SAMPLES:i]

  # Get the bits from the received signal
  rx_data = decode(carrier_filtered_new, Fs, symbolrate, bitspersym, SAMP_PER_SYMBOL)
  data_str = ''.join(str(i) for i in rx_data)

  # Detect all zero false positive
  if data_str.lstrip('0') != '':
    # Detect errors if valid signal
    error_code = crc_remainder(data_str, '11011')
    # error_flag true if no error
    if error_code == '0000':
      error_flag = True
    else:
      error_flag = False
    print error_code, error_flag
  else: 
    print 'Invalid Signal'
    error_flag = False
  
  return data_str[:-4], error_flag
