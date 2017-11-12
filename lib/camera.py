#!/usr/bin/env python
# Created by br@re-web.eu, 2015
# Modified by ferdinand _at_ zickner _dot_ de, 2017

import subprocess
import os
import pwd
import grp
import re

gphoto2cffi_enabled = False
piggyphoto_enabled = False

try:
    import piggyphoto as gp
    gpExcept = gp.libgphoto2error
    piggyphoto_enabled = True
    print('Info: Piggyphoto available')
except ImportError:
    print("Info: Piggyphoto isn't installed")
    pass

if not piggyphoto_enabled:
    try:
        import gphoto2cffi as gp
        gpExcept = gp.errors.GPhoto2Error
        gphoto2cffi_enabled = True
        print('Info: Gphoto2cffi available')
    except ImportError:
        print("Info: Gphoto2cffi isn't installed")
        pass

class CameraException(Exception):
    """Custom exception class to handle camera class errors"""
    def __init__(self, message, recoverable=False):
        self.message = message
        self.recoverable = recoverable

class Camera_gPhoto:
    """Camera class providing functionality to take pictures using gPhoto 2"""

    def __init__(self, config):
        self.config = config
        self.c = None
        self.get_camera()
        self.uid = pwd.getpwnam("pi").pw_uid
        self.gid = grp.getgrnam("pi").gr_gid

    def get_camera(self):
        # Print the capabilities of the connected camera
        try:
            if piggyphoto_enabled:
                self.c = gp.camera()
                if self.has_camera():
                    print(self.c.abilities)
            elif gphoto2cffi_enabled:
                self.c = gp.Camera()
            else:
                print(self.call_gphoto("-a", "/dev/null"))
        except CameraException as e:
            print('Warning: Listing camera capabilities failed (' + e.message + ')')
        except gpExcept as e:
            print('Warning: Listing camera capabilities failed (' + e.message + ')')

    def call_gphoto(self, action, filename):
        # Try to run the command
        try:
            cmd = "gphoto2 --force-overwrite --quiet " + action + " --filename " + filename
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            if "ERROR" in output:
                raise subprocess.CalledProcessError(returncode=0, cmd=cmd, output=output)
        except subprocess.CalledProcessError as e:
            if "EOS Capture failed: 2019" in e.output or "Perhaps no focus" in e.output:
                raise CameraException("Can't focus!\nMove a little bit!", True)
            elif "No camera found" in e.output:
                raise CameraException("No (supported) camera detected!", False)
            elif "command not found" in e.output:
                raise CameraException("gPhoto2 not found!", False)
            else:
                raise CameraException("Unknown error!\n" + '\n'.join(e.output.split('\n')[1:3]), False)
        return output

    def has_preview(self):
        return gphoto2cffi_enabled or piggyphoto_enabled

    def has_camera(self):
        return (gphoto2cffi_enabled or piggyphoto_enabled) and self.c is not None

    def status(self):
        self.batteryLevel = 0
        try:
            test = self.c.summary
        except:
            print("Camera connection lost! Restarting camera interface!")
            self.c.exit()
            self.c = None
            self.get_camera()

        if self.has_camera():
            self.batteryLevel = re.compile('^.*:([0-9]*).*$').match(str(self.c.config["main"]["status"]["batterylevel"])).group(1)
            if self.batteryLevel < 50:
                return False
        else:
            return False

        return True

    def take_preview(self, filename="/tmp/preview.jpg"):
        if gphoto2cffi_enabled:
            self._save_picture(filename, self.c.get_preview())
        elif piggyphoto_enabled:
            self.c.capture_preview(filename)
        else:
            raise CameraException("No preview supported!")

    def take_picture(self, filename="/tmp/picture.jpg"):
        if gphoto2cffi_enabled:
            print("gphoto2cffi: " + filename)
            self._save_picture(filename, self.c.capture())
        elif piggyphoto_enabled:
            print("piggyphoto: " + filename)
            filename_tmp="picture.jpg"
            self.c.capture_image(filename_tmp)
            os.rename(filename_tmp, filename)
        else:
            print("gphoto2: " + filename)
            self.call_gphoto("--capture-image-and-download", filename)
        os.chown(filename, self.uid, self.gid)
        return filename

    def _save_picture(self, filename, data):
        f = open(filename, 'wb')
        f.write(data)
        f.close()

    def set_idle(self):
        if gphoto2cffi_enabled:
            self.c._get_config()['actions']['viewfinder'].set(False)
        elif piggyphoto_enabled:
            # This doesn't work...
            self.c.config.main.actions.viewfinder.value = 0

    def close(self):
        if piggyphoto_enabled and 'c' in locals():
            self.c.exit()
