#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This class will process the request and prepare the response 

Created on Sat Apr 24 11:28:18 2021

@author: tapis
"""
import json
from threading import Lock


class HTTPRequestResponseProcessor:
    headers = {
        'Server': 'CrudeServer',
        'Content-Type': 'text/html',
    }

    status_codes = {
        200: 'OK',
        404: 'Not Found',
        501: 'Not Implemented',
    }
    
    def __init__(self, config_file_name):
        """
        Constructor method 

        Parameters
        ----------
        config_file_name : TYPE
            DESCRIPTION.
            Name of configuration file where request mapping is defined

        Returns
        -------
        None.

        """
        self.config_file_name = config_file_name
        self.lock = Lock()
        
        with open(config_file_name, "r") as config_file:
            self.config = json.load(config_file)
    
    def handle_request(self, request):
        """
        This method will identify the request method and pass the request to 
        appropriate request handler

        Parameters
        ----------
        request : TYPE
            DESCRIPTION.
            Request to be processed

        Returns
        -------
        response : TYPE
            DESCRIPTION.

        """
        try:
            handler = getattr(self, 'handle_%s' % request.method)
        except AttributeError:
            handler = self.HTTP_501_handler
        response = handler(request)
        return response
    
    def handle_GET(self,request):
        """
        Process GET request

        Parameters
        ----------
        request : TYPE
            DESCRIPTION.
            Request to be processed
            
        Returns
        -------
        TYPE
            DESCRIPTION.
            Prepared Response

        """
        response = None
        try:
            reqMap = self.getPathMapping(request.path)
            if reqMap['type'] == 'text':
                response = reqMap['response'];
            else:
                response = self.readResponseFromFile(reqMap['response'])
        except:
            pass
        return self.prepareResonse(response)
    
    def handle_POST(self, request):
        
        """
        Process POST request

        Parameters
        ----------
        request : TYPE
            DESCRIPTION.
            Request to be processed
            
        Returns
        -------
        TYPE
            DESCRIPTION.
            Prepared Response

        """
        response = None
        if request.path == '/resource/add':
            try:
                reqMap = json.loads(request.body)
                if self.getPathMapping(reqMap['requestPath']) == None:
                    self.config['requestMapping'].append(reqMap)
                    self.writeConfig()
                    response = '{"requestPath": "'+ reqMap['requestPath'] +'" , "status" : "SUCCESS" , "message" : "Created"}'
                else:
                    response = '{"requestPath": "'+ reqMap['requestPath'] +'" , "status" : "FAILED" , "message" : "Already Exist"}'
            except:
                pass
        return self.prepareResonse(response,{'Content-Type': 'application/json'})
        
    def writeConfig(self):
        """
        Write and update the request mapping configuration file.
        Calling method will change the self.config and call this method 
        to write the changed value to file

        Returns
        -------
        None.

        """
        self.lock.acquire()
        with open(self.config_file_name, "w") as config_file:
            json.dump(self.config, config_file,indent=4)
        self.lock.release()
            
    def getPathMapping(self,path):
        """
        Find the request mapping against the path provided

        Parameters
        ----------
        path : TYPE
            DESCRIPTION.
            Path for which request mapping to be found

        Returns
        -------
        reqMap : TYPE
            DESCRIPTION.
            Request mapping if found otherwise None

        """
        for reqMap in self.config['requestMapping']:
                if reqMap['requestPath'] == path:
                    return reqMap
        return None

    def handle_PUT(self,request):
        """
        Process PUT request

        Parameters
        ----------
        request : TYPE
            DESCRIPTION.
            Request to be processed
            
        Returns
        -------
        TYPE
            DESCRIPTION.
            Prepared Response

        """
        response = None
        if request.path == '/resource/update':
            try:
                reqMap = json.loads(request.body)
                prePath = self.getPathMapping(reqMap['requestPath']) 
                if prePath != None:
                    prePath['type'] = reqMap['type']
                    prePath['response'] = reqMap['response']
                    self.writeConfig()
                    response = '{"requestPath": "'+ reqMap['requestPath'] +'" , "status" : "SUCCESS" , "message" : "Updated"}'
                else:
                    response = '{"requestPath": "'+ reqMap['requestPath'] +'" , "status" : "FAILED" , "message" : "Not Exist"}'
            except:
                pass
        return self.prepareResonse(response,{'Content-Type': 'application/json'})
    
    def handle_HEAD(self,request):
        """
        Process HEAD request

        Parameters
        ----------
        request : TYPE
            DESCRIPTION.
            Request to be processed
            
        Returns
        -------
        TYPE
            DESCRIPTION.
            Prepared Response

        """
        headers = self.response_headers()
        blank_line = b"\r\n"
        response_line = self.response_line(200)
        return b"".join([response_line, headers, blank_line])
    
    def prepareResonse(self,response,extra_headers = None):
        """
        Prepare the reponse 

        Parameters
        ----------
        response : TYPE
            DESCRIPTION.
            Response body
            
        extra_headers : TYPE, optional
            DESCRIPTION. The default is None.
            Headers to be added while preparing response

        Returns
        -------
        TYPE
            DESCRIPTION.
            Prepared response

        """
        response_body = b""
        if response != None:
            response_body = response.encode()
        else:
            response_body = b"<h1>404 Not Found</h1>"
        response_line = self.response_line(200)
        headers = self.response_headers(extra_headers)
        blank_line = b"\r\n"
        return b"".join([response_line, headers, blank_line, response_body])
        
    def readResponseFromFile(self,filename):
        """
        Reading response from file.

        Parameters
        ----------
        filename : TYPE
            DESCRIPTION.
            Name of file.
            
        Returns
        -------
        TYPE
            DESCRIPTION.
            Read response from file.

        """
        try:
            with open(filename, 'r') as f:
                return f.read()    
        except :
            pass
        return None
    
    def response_line(self, status_code):
        """
        Returns response line

        Parameters
        ----------
        status_code : TYPE
            DESCRIPTION.
            Response Status Code
        Returns
        -------
        TYPE
            DESCRIPTION.
            Prepared response line
        """
        reason = self.status_codes[status_code]
        line = "HTTP/1.1 %s %s\r\n" % (status_code, reason)

        return line.encode() # call encode to convert str to bytes

    def response_headers(self, extra_headers=None):
        """
        Returns headers

        Parameters
        ----------
        extra_headers : TYPE, optional
            DESCRIPTION. The default is None.
            The `extra_headers` can be a dict for sending 
            extra headers for the current response
        Returns
        -------
        TYPE
            DESCRIPTION.
            Prepared response headers

        """
       
        headers_copy = self.headers.copy() # make a local copy of headers

        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ""

        for h in headers_copy:
            headers += "%s: %s\r\n" % (h, headers_copy[h])

        return headers.encode() # call encode to convert str to bytes
    
    def HTTP_501_handler(self, request):
        """
        Handler for not implemented methods

        Parameters
        ----------
        request : TYPE
            DESCRIPTION.
            Request to be handled

        Returns
        -------
        TYPE
            DESCRIPTION.
            Response

        """
        response_line = self.response_line(status_code=501)

        response_headers = self.response_headers()

        blank_line = b"\r\n"

        response_body = b"<h1>501 Not Implemented</h1>"

        return b"".join([response_line, response_headers, blank_line, response_body])
        
