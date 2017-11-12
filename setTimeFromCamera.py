#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by ferdinand _at_ zickner _dot_ de, 2017

from lib.camera import CameraException, Camera_gPhoto as CameraModule
from lib.events import Rpi_GPIO as GPIO
from lib.display import GUI_PyGame as GuiModule

import os
import json
from subprocess import call
from datetime import datetime
from glob import glob
from sys import exit
from time import sleep, clock

class TimeFromCamera:
    def __init__(self, config):
        self.config         = config
        self.gpio           = GPIO(self.handle_gpio, self.config["gpio"])

    def getTime(self):
        # Check for Camera
        self.camera = CameraModule(self.config["camera"])
        while not self.camera.has_camera():
            self.gpio.setMode("error")
            sleep(10)
            self.camera.get_camera()
        try:    dateCamera = str(self.camera.c.config["main"]["settings"]["datetimeutc"]).split("Date:")[1]
        except: dateCamera = False
        self.camera.close()
        return dateCamera

    def set(self):
        # Get Seconds since starting
        self.gpio.setMode("off")
        uptimeSeconds = -1
        with open('/proc/uptime', 'r') as f:
            uptimeSeconds = float(f.readline().split()[0])

        if uptimeSeconds <= 300 or "no" in os.popen("timedatectl status |grep \"NTP synchronized\"").read():
            dateCamera = self.getTime()
            if dateCamera:
                print("Current Sytstem time:     " + datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
                print("Setting date from Camera: " + datetime.fromtimestamp(float(dateCamera)).strftime('%d.%m.%Y %H:%M:%S'))
                try:
                    call("sudo date +%s -s @"+ dateCamera + " &> /dev/null", shell=True)
                    sleep(1)
                    print("New Sytstem time:         " + datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
                except:
                    print("Setting system time failed!")

                sleep(4)
        else:
            print("Time is correctly.")

    def handle_gpio(self, channel):
        print(channel)

    def teardown(self):
        self.gpio.teardown()

def main():
    with open('config.json', 'r') as f:
        config = json.load(f)
    if config:
        timeFromCamera = TimeFromCamera(config)
        timeFromCamera.set()
        timeFromCamera.teardown()
        return 0
    else:
        print("Error: Read config failed!")
        return 1

if __name__ == "__main__":
    exit(main())
