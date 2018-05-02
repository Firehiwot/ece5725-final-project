import RPi.GPIO as GPIO

CLK_PIN = 12
MISO_PIN = 16
MOSI_PIN = 20
CS_PIN = 21

GPIO.setmode(GPIO.BCM)

GPIO.setup(CLK_PIN, GPIO.OUT)
GPIO.setup(MISO_PIN, GPIO.IN)
GPIO.setup(MOSI_PIN, GPIO.OUT)
GPIO.setup(CS_PIN, GPIO.OUT)

def read_adc(adc_channel):
    if (adc_channel > 7 or adc_channel < 0):
        return -1

    GPIO.output(CS_PIN, True)

    # Start clock low and bring chip select low
    GPIO.output(CLK_PIN, False)
    GPIO.output(CS_PIN, False)

    # Set the chip select to the appropriate channel
    commandout = adc_channel
    commandout |= 0x18
    commandout <<= 3
    for i in range(5):
        if commandout & 0x80:
            GPIO.output(MOSI_PIN, True)
        else:
            GPIO.output(MOSI_PIN, False)
        commandout <<= 1

        # Toggle clock
        GPIO.output(CLK_PIN, True)
        GPIO.output(CLK_PIN, False)

    # Get the adc output. Read in one empty bit, one null bit, and 10 ADC bits.
    adc_out = 0
    for i in range(12):
        # Toggle clock
        GPIO.output(CLK_PIN, True)
        GPIO.output(CLK_PIN, False)
        
        # Read in a bit
        adc_out <<= 1
        if GPIO.input(MISO_PIN):
            adc_out |= 0x1

    # Bring chip select high
    GPIO.output(CS_PIN, True)

    # Drop the first bit since it's null
    adc_out >>= 1

    return adc_out
