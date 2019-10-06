#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by ferdinand _at_ zickner _dot_ de, 2017

from lib.camera import CameraException, Camera_gPhoto as CameraModule
from lib.events import Rpi_GPIO as GPIO
from lib.display import GUI_PyGame as GuiModule
from lib.picture import PictureList
from lib.slideshow import Slideshow

from datetime import datetime
from glob import glob
from sys import exit
from time import sleep, clock, time
from PIL import Image
from threading import Thread
import os
import json


class FotoBox:
    def __init__(self, config):
        self.config         = config
        self.display        = GuiModule(self.config["display"])
        self.pictures       = PictureList(self.config["pictures"])
        self.gpio           = GPIO(self.handle_gpio, self.config["gpio"])
        self.camera         = CameraModule(self.config["camera"])
        self.check_camera()

    def _run_plain(self):
        while True:
            #self.camera.set_idle()

            # Display default message
            # self.display.clear()
            self.display.show_message(self.config["messages"]["interact"])
            self.display.apply()

            # Wait for an event and handle it
            event = self.display.wait_for_event()
            self.handle_event(event)

    def run(self):
        while True:
            try:
                self._run_plain()

            # Catch exceptions and display message
            except CameraException as e:
                self.handle_exception(e.message)
            # Do not catch KeyboardInterrupt and SystemExit
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                print('SERIOUS ERROR: ' + repr(e))
                self.handle_exception("SERIOUS ERROR!")
                self.teardown(True)

    def take_single_picture(self):
        """Implements the picture taking routine"""
        # Show pose message
        self.gpio.setMode("captureImage")
        self.display.clear()
        #self.display.show_message("POSE!\n\nTaking a picture!");
        self.display.apply()
        sleep(4)

        # Try each picture up to 3 times
        remaining_attempts = 3
        while remaining_attempts > 0:
            remaining_attempts = remaining_attempts - 1
            try:
                output_filename = self.pictures.get_next()
                outfile = self.camera.take_picture(output_filename)
                remaining_attempts = 0
            except CameraException as e:
                # On recoverable errors: display message and retry
                if e.recoverable:
                    if remaining_attempts > 0:

                        self.display.show_message(e.message)
                        self.display.apply()
                        sleep(5)
                    else:
                        raise CameraException("Giving up! Please start over!", False)
                else:
                    raise e

        # Show picture
        self.display.clear()
        self.display.show_picture(output_filename)
        self.display.apply()
        self.gpio.setMode("rainbow")
        sleep(2)

    def teardown(self, error=False, system_shutdown=False):
        self.display.clear()
        self.display.show_background()
        self.display.show_message("Shutting down...")
        self.display.apply()
        self.camera.close()
        self.gpio.teardown()
        sleep(0.5)
        self.display.teardown()
        if system_shutdown:
            exit(12)
        else:
            exit(0)

    def event_main_key(self):
        if self.camera.has_camera():
            if self.camera.status():
                self.take_single_picture()
            else:
                if self.camera.batteryLevel == 0:
                    self.check_camera()
                else:
                    self.showError(self.config["messages"]["camera_change_battery"] + " ()" + self.camera.batteryLevel + " %)")
        else:
            self.camera.get_camera()

    def handle_event(self, event):
        if event.type == 0:
            self.teardown()
        elif event.type == 1:
            self.handle_keypress(event.value)
        elif event.type == 2:
            self.handle_mousebutton(event.value[0], event.value[1])
        elif event.type == 3:
            self.handle_gpio_event(event.value)

    def handle_keypress(self, key):
        """Implements the actions for the different keypress events"""
        # Exit the application
        if key == ord('q'):
            self.teardown()
        # Take pictures
        elif key == ord('b'):
            self.event_main_key()
        elif key == ord('c'):
            self.event_main_key()
        # Search Camera
        elif key == ord('s'):
            self.camera.get_camera()

    def handle_mousebutton(self, key, pos):
        """Implements the actions for the different mousebutton events"""
        # Take a picture
        if key < 10:
            self.event_main_key()

    def handle_gpio(self, channel):
        if channel in self.config["gpio"]["input_channels"].values():
            if channel == self.config["gpio"]["input_channels"]["shutdown"]:
                print("Shutdown by GPIO")
                self.teardown(False, True)

    def handle_exception(self, msg):
        """Displays an error message and returns"""
        self.gpio.setMode("error")
        self.display.clear()
        self.display.show_background()
        print("Error: " + msg)
        self.display.show_message("ERROR:\n\n" + msg)
        self.display.apply()
        sleep(3)

    def check_camera(self):
        # Check for Camera
        while not self.camera.has_camera():
            self.showError(self.config["messages"]["no_camera"])

        self.gpio.setMode("rainbow")
        self.display.clear()
        self.display.show_background()
        self.display.apply()

    def showError(self, message):
        self.gpio.setMode("error")
        self.display.clear()
        self.display.show_background()
        self.display.show_message(message)
        self.display.apply()

        # Wait for an event and handle it
        event = self.display.wait_for_event()
        self.handle_event(event)

def main():
    with open('config.json', 'r') as f:
        config = json.load(f)
    if config:
        fotobox = FotoBox(config)
        fotobox.run()
        fotobox.teardown()
        return 0
    else:
        print("Error: Read config failed!")
        return 1

if __name__ == "__main__":
    exit(main())
