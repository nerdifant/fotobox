#!/usr/bin/env python

import urllib
import urllib2
import json
import ssl

class SeaFile:
    def __init__(self, config):
        self.url = config['url']
        self.auth = config['auth']
        self.context = ssl._create_unverified_context()

        # Post seafile email/password to obtain auth token.
        data = urllib.urlencode(self.auth)
        try:
            self.token = self._api2("auth-token/", data)['token']
        except:
            print("[Error]: Connection to seafile server failed.")

        # Test connection and get repo
        if hasattr(self, 'token'):
            self.repo = self._get_repo(config['repo'])
            if self.repo:
                self.shared_link_expire = config['shared_link_expire']
                self.shared_link_password = config['shared_link_password']

        return None

    def _api2(self, path, data = None, reqType = False):
        req = urllib2.Request(self.url + "/api2/" + path, data)
        if hasattr(self, 'token'): req.add_header('Authorization', 'Token ' + self.token)
        if reqType: req.get_method = lambda: reqType

        try:
            response = urllib2.urlopen(req, context = self.context)
        except:
            return False

        page = response.read()
        if page == "":
            return response.info()
        else:
            return json.loads(page)

    def ping(self):
        return "pong" == self._api2("auth/ping/")

    def _get_repo(self, name):
        repos =  self._api2("repos/")
        for repo in repos:
            if repo["name"] == name:
                return repo
        return False

    def get_share_link(self, path_file):
        ## Create Link
        values = {'p': path_file}
        if self.shared_link_expire > 0: values["expire"] = self.shared_link_expire    # days
        if self.shared_link_password: values["password"] = self.shared_link_password
        data = urllib.urlencode(values)
        self._api2("repos/" + self.repo["id"] + "/file/shared-link/", data, "PUT")

        ## Get Link
        fileshares = self._api2("shared-links/")["fileshares"]
        for f in fileshares:
            if f["repo_id"] == self.repo["id"] and f["path"] == path_file:
                return self.url + "/f/" + f["token"]


def main():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    if config:
        for seaf_conf in config["seafile-servers"]:
            # Test Seafile
            seafile = SeaFile(seaf_conf)
            if seafile.ping():
                print seafile.get_share_link("/2017-06-24/pic00004.jpg")
        return 0
    else:
        print("Error: Read config failed!")
        return 1

if __name__ == "__main__":
    exit(main())
