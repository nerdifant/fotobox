﻿#!/usr/bin/env python

import urllib
import urllib2
import json
import ssl
import ccnet
import seafile
from time import sleep

class SeafileClient:
    def __init__(self, configs):
        for config in configs:
            self.enabled = config['enabled']
            self.url = config['url']
            self.auth = config['auth']
            self.conf_dir = config['conf_dir']
            self.context = ssl._create_unverified_context()

            if self.enabled:
                # Post seafile email/password to obtain auth token.
                data = urllib.urlencode(self.auth)
                try:
                    self.token = json.loads(self.urlopen("auth-token/", data))['token']
                except:
                    print("[Error]: Connection to seafile server failed.")

                    # Test connection and get repo
                    if hasattr(self, 'token'):
                        self.repo = self._get_repo(config['repo'])
                        if self.repo:
                            self.shared_link_expire = config['shared_link_expire']
                            self.shared_link_password = config['shared_link_password']
                            return

    def urlopen(self, path, data = None, reqType = False):
        req = urllib2.Request(self.url + "/api2/" + path, data)
        if hasattr(self, 'token'): req.add_header('Authorization', 'Token ' + self.token)
        if reqType: req.get_method = lambda: reqType
        try:    resp = urllib2.urlopen(req, context = self.context)
        except: return False
        return resp.read()

    def ping(self):
        if self.enabled:
            return "pong" == json.loads(self.urlopen("auth/ping/"))
        else:
            return False

    def status(self):
        pool = ccnet.ClientPool(self.conf_dir)
        seafile_rpc = seafile.RpcClient(pool, req_pool=False)
        t = seafile_rpc.get_repo_sync_task(self.repo["id"])
        if not t:
            return "waiting for sync"
        else:
            return t.state

    def _get_repo(self, name):
        repos = json.loads(self.urlopen("repos/"))
        for repo in repos:
            if repo["name"] == name:
                return repo
        return False

    def get_share_link(self, filename):
        ## Create Link
        values = {'p': filename}
        if self.shared_link_expire > 0: values["expire"] = self.shared_link_expire    # days
        if self.shared_link_password: values["password"] = self.shared_link_password
        data = urllib.urlencode(values)
        resp = self.urlopen("repos/" + self.repo["id"] + "/file/shared-link/", data, "PUT")
        if resp: print resp.info()

        ## Get Link
        fileshares = json.loads(self.urlopen("shared-links/"))["fileshares"]
        for f in fileshares:
            if f["repo_id"] == self.repo["id"] and f["path"] == filename:
                return self.url + "/f/" + f["token"]
        return False

    def wait_and_get_link(self, filename, time_in_seconds = 20):
        for i in range(time_in_seconds * 2):
            sleep(1)
            if self.status() == "synchronized":
                link = self.get_share_link(filename)
                if link:
                    return link
            sleep(0.5)


def main():
    with open('../config.json', 'r') as f:
        config = json.load(f)
    if config:
        seafile = SeafileClient(config["seafile-servers"])      # Uses the first working server
        if seafile.ping():
            print seafile.status()
            print seafile.get_share_link("/2017-06-24/pic00006.jpg")
        return 0
    else:
        print("Error: Read config failed!")
        return 1

if __name__ == "__main__":
    exit(main())
