#!/usr/bin/env python
# Created by br _at_ re-web _dot_ eu, 2015

try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    gpio_enabled = True
except ImportError:
    gpio_enabled = False


class Event:
    def __init__(self, type, value):
        """type  0: quit
                 1: keystroke
                 2: mouseclick
                 3: gpio
        """
        self.type = type
        self.value = value
        self.mode = "rainbow"

class Rpi_GPIO:
    def __init__(self, handle_function, config):
        self.config = config
        if gpio_enabled:
            # Display initial information
            print("Your Raspberry Pi is board revision " + str(GPIO.RPI_INFO['P1_REVISION']))
            print("RPi.GPIO version is " + str(GPIO.VERSION))

            # Choose BCM numbering system
            GPIO.setmode(GPIO.BCM)

            # Setup the input channels
            for channels in self.config["input_channels"].values():
                GPIO.setup(channels, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                GPIO.add_event_detect(channels, GPIO.RISING, callback=handle_function, bouncetime=200)

            # Setup the output channels
            for channels in self.config["output_channels"].values():
                GPIO.setup(channels, GPIO.OUT)
                GPIO.output(channels, GPIO.HIGH)
        else:
            print("Warning: RPi.GPIO could not be loaded. GPIO disabled.")

    def teardown(self):
        if gpio_enabled:
            for channel in self.config["output_channels"].values():
                self.setOutput(channel, 0)
            GPIO.cleanup()

    def setOutput(self, channel, value=0):
        if gpio_enabled and channel in self.config["output_channels"].values():
            GPIO.output(channel, GPIO.HIGH if value==1 else GPIO.LOW)

    def setMode(self, mode):
        self.mode = mode
        if self.mode == 'rainbow':
            self.setOutput(self.config["output_channels"]["led0"], 1)
            self.setOutput(self.config["output_channels"]["led1"], 1)
        elif self.mode == 'captureImage':
            self.setOutput(self.config["output_channels"]["led0"], 0)
            self.setOutput(self.config["output_channels"]["led1"], 1)
        elif self.mode == 'off':
            self.setOutput(self.config["output_channels"]["led0"], 0)
            self.setOutput(self.config["output_channels"]["led1"], 0)
        else:
            self.setOutput(self.config["output_channels"]["led0"], 1)
            self.setOutput(self.config["output_channels"]["led1"], 0)

    def getMode(self):
        return self.mode
