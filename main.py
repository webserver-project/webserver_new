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
import logging
import socket

default_config = {
    "host" : "127.0.0.1",
    "port" : 8888,
    "max_connections" : 5,
    "requestMappingFile" : "mapping.json",
    "threadCount" : 5,
    "logfile" : "server.log"
}

def main():
    """
    Execution will start from here

    Returns
    -------
    None.

    """
    server = None
    def handler(signal_received, frame):
        # Handle any cleanup here
        print('SIGINT or CTRL-C detected. Exiting...')
        if(server != None):
            server.shutdown()
        exit(0)
    signal(SIGINT, handler)
    config_file_name = "config.json"
    error = ""
    try:
        with open(config_file_name, "r") as config_file:
                try:
                    config = json.load(config_file)
                    fillDefault(config)
                except:
                    error = "Error in parsing confuration using default"
                    config = default_config
    except IOError:
        config = default_config
        error = "Error in opening confuration file using default"
    logging.basicConfig(filename=config["logfile"], format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
    if error != "":
       logging.warning(error)
    validateConfig(config)
    with ThreadPoolExecutor(config["threadCount"]) as executor:
        server = HTTPServer(config,executor)
        print("Starting Web Server")
        server.start()
        
def fillDefault(config):
    """
    If a config value not provided fill it with default

    Parameters
    ----------
    config : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if 'logfile' not in config:
        config['logfile'] = default_config['logfile']
    if 'host' not in config:
        config['host'] = default_config['host']
    if 'port' not in config:
        config['port'] = default_config['port']
    if 'max_connections' not in config:
        config['max_connections'] = default_config['max_connections']
    if 'requestMappingFile' not in config:
        config['requestMappingFile'] = default_config['requestMappingFile']
    if 'threadCount' not in config:
        config['threadCount'] = default_config['threadCount']
        
def validateConfig(config):
    """
    Validate configuration

    Parameters
    ----------
    config : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    try:
        socket.gethostbyname(config['host'])
    except:
        logging.error("Please check host in config. exiting....")
        exit(0)
    if  (not isinstance(config['port'], int)) or config['port'] < 1 or config['port'] > 65353:
        logging.error("Please check port in config. exiting...")
        exit(0)
    if not isinstance(config['max_connections'], int):
        logging.error("Max connection should be valid integer. exiting...")
        exit(0)
    if (not isinstance(config['threadCount'], int)) or config['threadCount'] < 1:
        logging.error("Max connection should be valid integer. exiting...")
        exit(0)
         
   
        
if __name__ == '__main__':
    main()
