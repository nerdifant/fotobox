# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
#
# https://tutorials-raspberrypi.de/raspberry-pi-ws2812-ws2811b-rgb-led-streifen-steuern/
# https://github.com/jgarff/rpi_ws281x

from functools import partial
from signal import *
from neopixel import *
import threading
import time
import socket
import sys
import atexit

class LED_ring(threading.Thread):
	def __init__(self):
		# LED strip configuration:
		self.led_count_in = 24		# Number of LED pixels in the inner ring.
		self.led_count_out = 32		# Number of LED pixels in the outer ring.
		self.numPixels = 96			# Virtual number of LED pixels.
		LED_PIN		= 18	  # GPIO pin connected to the pixels (18 uses PWM!).
		LED_FREQ_HZ	= 800000  # LED signal frequency in hertz (usually 800khz)
		LED_DMA		= 5	   # DMA channel to use for generating signal (try 5)
		LED_BRIGHTNESS = 8	  # Set to 0 for darkest and 255 for brightest
		LED_INVERT	 = False   # True to invert the signal (when using NPN transistor level shift)
		LED_CHANNEL	= 0	   # set to '1' for GPIOs 13, 19, 41, 45 or 53
		LED_STRIP	  = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

		# Create NeoPixel object with appropriate configuration. Intialize the library (must be called once before other functions).
		self.led = Adafruit_NeoPixel(self.led_count_in + self.led_count_out, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
		self.led.begin()

		self.stopped = False
		self.mode = "rainbow"
		self.rainbow_last_pos = 0
		threading.Thread.__init__(self)

	def run(self):
		while not self.stopped:
			if self.mode == 'countdown':
				self.countdown(Color(0, 127, 0))
			elif self.mode == 'finished':
				self.rainbowRotateFill(Color(127, 0, 0))
				self.flash(Color(0, 255, 0))
				self.mode = 'rainbow'
			elif self.mode == 'rainbow':
				self.rainbow()
			elif self.mode == 'off':
				self._setRingColor(Color(0, 0, 0))
				self.led.show()
			else:
				self.flash(Color(255, 0, 0), 1)

	def close(self):
		self.stopped = True

	def set(self, mode):
		self.mode = mode

	def _setPixelColorCycle(self, pos, color, innerRing=True, outerRing=True):
		pos = (pos + 44) % self.numPixels
		if innerRing and (pos % 4) == 0: ## Inner ring
			self.led.setPixelColor(pos/4, color)
		if outerRing and (pos % 3) == 0: ## Outer ring
			self.led.setPixelColor(24+pos/3, color)

	def _setRingColor(self, color, innerRing=True, outerRing=True):
		for i in range(self.numPixels):
			self._setPixelColorCycle(i, color, innerRing, outerRing)

	def _wheel(self, pos):
		"""Generate rainbow colors across 0-255 positions."""
		if pos < 85:
			return Color(pos * 3, 255 - pos * 3, 0)
		elif pos < 170:
			pos -= 85
			return Color(255 - pos * 3, 0, pos * 3)
		else:
			pos -= 170
			return Color(0, pos * 3, 255 - pos * 3)

	def countdown(self, color):
		# Countdown
		for i in range(24):
			self._setPixelColorCycle(self.numPixels - (i * 4), Color(0, 0, 0), True, False)
			if i % 2 == 0:
				self._setRingColor(color, False)
			else:
				self._setRingColor(Color(0, 0, 0), False)
			self.led.show()
			time.sleep(0.2)

		# Flash
		self._setRingColor(Color(255, 255, 255)) # All lights on
		self.led.show()
		time.sleep(0.5)

		# Waiting Rainbow
		i = 0
		while True:
			self._setPixelColorCycle(i, Color(0, 0, 0), True, False)
			self._setPixelColorCycle(self.numPixels-i, Color(0, 0, 0), False)
			for j in range(20):
				self._setPixelColorCycle(i + 1 + j,
				 	self._wheel(int((i + 1 + j) * 256 / self.numPixels) % 255), True, False)
				self._setPixelColorCycle(self.numPixels - i - 1 - j,
					self._wheel(int((self.numPixels - i - 1 - j) * 256 / self.numPixels) % 255), False)
			self.led.show()
			self.rainbow_last_pos = i = i + 1
			time.sleep(0.02)
			if self.mode != "countdown" or self.stopped:
				return

	def rainbow(self, iterations=1):
		# rotating rainbow
		for offset in range(256*iterations):
			for i in range(self.numPixels):
				self._setPixelColorCycle(i, self._wheel((int(i * 256 / self.numPixels) + offset) & 255))
			self.led.show()
			time.sleep(0.02)
			if self.mode != "rainbow" or self.stopped:
				return

	def rainbowRotateFill(self, color, length=20):
		start = self.rainbow_last_pos % self.numPixels
		for i in range(self.numPixels - length + 1):
			self._setPixelColorCycle(i + length + start,
				self._wheel(int(( i + length + start) * 256 / self.numPixels) % 255), True, False)
			self._setPixelColorCycle(self.numPixels - i - length - start,
				self._wheel(int((self.numPixels - i - length - start) * 256 / self.numPixels) % 255), False)
			self.led.show()
			time.sleep(0.02)

	def flash(self, color, iterations=3):
		for i in range(iterations):
			self._setRingColor(Color(0, 0, 0))
			self.led.show()
			time.sleep(0.2)
			self._setRingColor(color)
			self.led.show()
			time.sleep(0.2)

def close(*args):
	sock.close()
	led._setRingColor(Color(0, 0, 0))
	led.led.show()
	led.close()
	print "Closing LED server."
	sys.exit(0)

# Main program logic follows:
if __name__ == '__main__':

	for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
	    signal(sig, close)

	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Bind the socket to the port
	server_address = ('localhost', 10000)
	print 'Starting up on %s port %s' % server_address
	sock.bind(server_address)

	# Listen for incoming connections
	sock.listen(1)

	# Starting LED ring
	led = LED_ring()
	led.start()

	#print ('Press Ctrl-C to quit.')
	while True:
		# Wait for a connection
		print 'waiting for a connection'
		connection, client_address = sock.accept()
		try:
			print 'connection from', client_address

			# Receive the data in small chunks and retransmit it
			while True:
				data = connection.recv(16)
				print 'received "%s"' % data
				if data:
					print 'sending data back to the client'
					connection.sendall(data)
					led.set(data)
				else:
					print >>sys.stderr, 'no more data from', client_address
					break

		finally:
			# Clean up the connection
			connection.close()

	led.stop()
