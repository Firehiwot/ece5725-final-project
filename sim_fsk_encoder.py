#
# sim_fsk_encoder.py
# Angus Gibbs (aag233) and Joao Pedro Carvao (jc2697)
#
# Generates simulated signal for FSK testing.
#

import numpy as np
import matplotlib.pyplot as pyplot

Fs   = 860.0                      # sampling frequency 
Fc   = 250.0                      # carrier frequency
Fdev = 100.0                      # deviation from carrier frequency for FSK 
bitrate = 1.0                     # bits/sec
samp_per_bit = int(Fs/bitrate)    # duration of one representation 
numbits = 128
duration = samp_per_bit * numbits # duration of whole signal in samples

# Generate random bits
bits = np.random.random_integers(0, 1, numbits)

# Voltage controlled oscillator (VCO)  
m = []
for bit in bits:
  if bit == 0:
    m += [Fc-Fdev]*samp_per_bit
  else:
    m += [Fc+Fdev]*samp_per_bit
   
# Array for easy operations
m = np.array(m)

# Generate carrier frequency 
t = np.arange(0, numbits/bitrate , 1/Fs, dtype=np.float)

# Generate the carrier signal
amp = 1
carrier = amp*np.cos(2*np.pi * m * t)

# Add Gaussian white noise to carrier signal
amp_noise = 0.1
noise = np.random.randn(len(carrier))*amp_noise
carrier = np.add(carrier, noise)

# Plot the bits and the encoded signal
pyplot.subplot(2,1,1)
pyplot.plot(carrier)
pyplot.subplot(2,1,2)
pyplot.plot(bits)
pyplot.show()
