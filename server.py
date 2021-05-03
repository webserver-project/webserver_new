#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This class will be responsible for creating server and accepting request
and pass the request to appropriate module to parse and process the request

Created on Sat Apr 24 08:24:44 2021

@author: tapis
"""

# main.py 
import socket
from request_parser import HTTPRequestParser
from request_response_processor import HTTPRequestResponseProcessor
import logging

BUFF_SIZE = 4096

class HTTPServer:

    def __init__(self, config , executor):
        self.config = config
        self.executor = executor
        logging.basicConfig(filename=self.config["logfile"], format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)
        
    def start(self):
        """
        Start the serevr  

        Returns
        -------
        None.

        """
        # create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind the socket object to the address and port
        s.bind((self.config['host'], self.config['port']))
        # start listening for connections
        s.listen(self.config['max_connections'])
        
        self.server_socket = s
        
        logging.info("Listening at" + str(s.getsockname()))
        
        #create a response processor
        responseProcessor = HTTPRequestResponseProcessor(self.config['requestMappingFile'])    
        
        while True:
            # accept any new connection
            conn, addr = s.accept()
            arg = {'conn' : conn, 'addr' : addr, 'responseProcessor' : responseProcessor}
            #Submit to thread pool 
            self.executor.submit(self.handle_request,(arg))
    
    def shutdown(self):
        """
        Server shutdown

        Returns
        -------
        None.

        """
        self.server_socket.close()    
        
    def recvall(self,conn):
        """
        This is utility method for server to receive all data from the connection

        Parameters
        ----------
        conn : TYPE
            DESCRIPTION.
            Connection from which data to be read
            
        Returns
        -------
        data : TYPE
            DESCRIPTION.
            Data after read

        """
        data = b''
        while True:
            part = conn.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                # either 0 or end of data
                break
        return data
    
        
    def handle_request(self, arg):
        """
        This method will be the entry point of the request.

        Parameters
        ----------
        arg : TYPE
            DESCRIPTION.
            It is a dictionary containing all information for processing the request
            It containd below information
                1. Connection object
                2. Address of remote machine
                3. Response processor object
        Returns
        -------
        None.

        """
        conn = arg['conn']
        addr = arg['addr'] 
        responseProcessor = arg['responseProcessor']
        try:
            logging.info("Connected by: " + str(addr))
            data = self.recvall(conn)
            logging.info("Received HTTP Request: \n" + str(data))
            request = HTTPRequestParser(data)
            logging.info("Request Line: " + str(request.line))
            logging.info("Request Headers: " + str(request.headers))
            logging.info("Request Body: \n" + str(request.body)) 
            logging.info("Request Method: "+ str(request.method))
            logging.info("Request Path: "+ str(request.path))
            logging.info("HTTP Version: "+ str(request.http_version))
            response = responseProcessor.handle_request(request)
            logging.info("Sending Response:\n"+ str(response))
            conn.sendall(response)
            conn.close()
        except Exception as e: logging.info(e)

