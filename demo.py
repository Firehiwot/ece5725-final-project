#
# capture_transmission.py
# Angus Gibbs (aag233) and Joao Pedro Carvao (jc2697)
#
# PiTFT script demoing communication system.
#

import os
import pygame
import sys
import time
import numpy as np
import RPi.GPIO as GPIO

from mcp3008 import read_adc
import fsk_demod_lib

# Flag to play demo on PiTFT Screen
if '--real' in sys.argv:
  # Set up environment variables to display on PiTFT
  os.putenv('SDL_VIDEODRIVER', 'fbcon')
  os.putenv('SDL_FBDEV', '/dev/fb1')
  os.putenv('SDL_MOUSEDRV', 'TSLIB')
  os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

# Set up GPIO inputs
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Keep track of button state
should_quit = False
mute = False

# Callbacks for button presses
def quit_cb(channel):
  # Toggle the quit flag
  global should_quit
  should_quit = True

def mute_cb(channel):
  # Toggle the mute flag
  global mute 
  mute = not mute

  # Refresh the display if needed
  if state == "display":
    display_bits()    

# Listen for the button presses
GPIO.add_event_detect(27, GPIO.FALLING, callback=quit_cb, bouncetime=300)
GPIO.add_event_detect(17, GPIO.FALLING, callback=mute_cb, bouncetime=300)

# Initialize pygame
pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((320, 240))

# Define colors
COLOR_WHITE = 255, 255, 255
COLOR_BLACK = 0, 0, 0
COLOR_RED = 255, 0, 0
COLOR_GREEN = 0, 255, 0

# Define fonts
font_face = pygame.font.Font(None, 40)
font_face_sm = pygame.font.Font(None, 18)

# Define images
listen_img = pygame.image.load("/home/pi/ece5725-final-project/img/listening_mic_icon.gif")
listen_small_img = pygame.image.load("/home/pi/ece5725-final-project/img/listening_mic_icon_small.gif")
mute_img = pygame.image.load("/home/pi/ece5725-final-project/img/mute_mic_icon.gif")
mute_small_img = pygame.image.load("/home/pi/ece5725-final-project/img/mute_mic_icon_small.gif")
capture_img = pygame.image.load("/home/pi/ece5725-final-project/img/capture_mic_icon.gif")

# Define the transmission characteristics
SAMPLING_RATE = 7500
M = 2 # number of bits per symbol
SYMBOL_RATE = 4
SAMP_PER_SYMBOL = SAMPLING_RATE / SYMBOL_RATE
HIGH_FREQ = 400  # Hz
LOW_FREQ = 300   # Hz 
PEAK_BANDWIDTH = 5  # Hz
AVG_BANDWIDTH = 30  # Hz
PEAK_HEIGHT = 1.4   # power

PREFIX_MULTIPLIER = 1  # adjust the length of start signal 
PREFIX_SAMPLES = PREFIX_MULTIPLIER*SAMPLING_RATE 
DATA_BITS = 32  # bits
CRC_BITS = 4
DATA_SAMPLES = (DATA_BITS / M) * SAMP_PER_SYMBOL
CRC_SAMPLES = (CRC_BITS / M) * SAMP_PER_SYMBOL
TRANSMISSION_LENGTH = PREFIX_SAMPLES + DATA_SAMPLES + CRC_SAMPLES + SAMP_PER_SYMBOL  # samples

# Keep a buffer of samples
start_buffer = [0] * SAMP_PER_SYMBOL
detected_buffer = [0] * TRANSMISSION_LENGTH

def sample_slot(arr, start_index=0):
  """
  Sample one time slot's worth of samples from the ADC.

  Arguments:
    arr (list): The array to put the samples in
    start_index (int, optional): The index at which to put the first sample
  """
  next_time = time.time()

  for i in range(SAMP_PER_SYMBOL):
    next_time = next_time + 1 / float(SAMPLING_RATE)

    while time.time() < next_time:
      pass

    arr[i+start_index] = read_adc(0)


def start_recording():
  """
  Buffer an entire transmission after the start of transmission is detected.
  """
  # Render image
  if state == "capture": 
    screen.fill(COLOR_BLACK)
    render_image(capture_img, 160, 120)
    pygame.display.flip()

  # Buffer transmission
  for samp in range(TRANSMISSION_LENGTH/SAMP_PER_SYMBOL):
    sample_slot(detected_buffer, (samp)*SAMP_PER_SYMBOL)


def parse_recording():
  """
  Find the end of the prefix and then pass the data samples to the decoder.
  """
  global outbits, crc

  # Decode the recording
  outbits, crc = fsk_demod_lib.demod(
    detected_buffer, SAMPLING_RATE, SYMBOL_RATE, DATA_SAMPLES, CRC_SAMPLES,
    SAMP_PER_SYMBOL, M
  )
  
  # Update the app state
  global state 
  state = "display"
  
  # Display the received bits
  display_bits()
  
  return outbits, crc

def display_bits():
  """
  Display bits (or an error message) on the PiTFT.
  """
  # Success and error screens
  if crc == True:
    screen.fill(COLOR_GREEN)
    render_text(outbits[8:20], COLOR_WHITE, (160, 100))
    render_text(outbits[20:],  COLOR_WHITE, (160, 140))
  else:
    screen.fill(COLOR_RED)
    render_text("ERROR", COLOR_BLACK, (160,120))
  
  # Show still listeing for signal
  if state == "display" and not mute:
     render_image(listen_small_img, 280, 200)
  elif state == "display":
    render_image(mute_small_img, 280, 200)

  pygame.display.flip()

def render_text(text, color, center):
  """
  Renders text on PiTFT screen.

  Arguments:
    text (str): The text to display
    color (tuple): The text color
    center (tuple): The x- and y-coordinates of the text center
  """
  surface = font_face.render(text, True, color)
  rect = surface.get_rect(center=center)
  screen.blit(surface, rect)

def render_image(img, x, y):
  """
  Renders image on the PiTFT.

  Arguments:
    img (object): The image to display
    x (int): The x-coordinate
    y (int): The y-coordinate
  """
  img_rect = img.get_rect()
  img_rect.centerx = x
  img_rect.centery = y
  screen.blit(img, img_rect)

# Keep track of program state
state = 'listening'  # listening, capture, display

# Continuously look for a start of transmission
while not should_quit:
  
  # Render the appropriate display
  if state == 'listening':
    if not mute:
      screen.fill(COLOR_BLACK)
      render_image(listen_img, 160, 120)
      pygame.display.flip()
    else:
      screen.fill(COLOR_BLACK)
      render_image(mute_img, 160, 120)
      pygame.display.flip()
  
  # Listen for the transmission
  if not mute:
    # Sample one slot's worth of samples from the ADC
    sample_slot(start_buffer)

    # Check if there has been a spike at the high and low frequencies,
    # indicating the start of a transmission
    fft = np.fft.fft(start_buffer)
    low_band_avg = np.mean(np.abs(fft[SYMBOL_RATE*LOW_FREQ-AVG_BANDWIDTH:
                      SYMBOL_RATE*LOW_FREQ+AVG_BANDWIDTH]))
    high_band_avg = np.mean(np.abs(fft[SYMBOL_RATE*HIGH_FREQ-AVG_BANDWIDTH:
                       SYMBOL_RATE*HIGH_FREQ+AVG_BANDWIDTH]))
    low_band_peak = np.mean(np.abs(fft[SYMBOL_RATE*LOW_FREQ-PEAK_BANDWIDTH:
                       SYMBOL_RATE*LOW_FREQ+PEAK_BANDWIDTH]))
    high_band_peak = np.mean(np.abs(fft[SYMBOL_RATE*HIGH_FREQ-PEAK_BANDWIDTH:
                      SYMBOL_RATE*HIGH_FREQ+PEAK_BANDWIDTH]))
    
    # Check for the spike
    if (high_band_peak > PEAK_HEIGHT*high_band_avg and
      low_band_peak > PEAK_HEIGHT*low_band_avg):
      state = "capture"
      start_recording()
      parse_recording()
