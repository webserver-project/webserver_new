#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main file from where execution will start

Created on Sat Apr 24 09:09:43 2021

@author: tapis
"""
from server import HTTPServer
from concurrent.futures import ThreadPoolExecutor
import json
from signal import signal, SIGINT
from sys import exit


def main():
    server = None
    def handler(signal_received, frame):
        # Handle any cleanup here
        print('SIGINT or CTRL-C detected. Exiting...')
        if(server != None):
            server.shutdown()
        exit(0)
    signal(SIGINT, handler)
    config_file_name = "config.json"
    with open(config_file_name, "r") as config_file:
            config = json.load(config_file)
            with ThreadPoolExecutor(config["threadCount"]) as executor:
                server = HTTPServer(config,executor)
                print("Starting Web Server")
                server.start()
if __name__ == '__main__':
    main()
