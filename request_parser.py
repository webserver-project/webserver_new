#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This class will parse the request
 
Created on Sat Apr 24 09:25:39 2021

@author: tapis
"""


class HTTPRequestParser:
    def __init__(self, request):
        request_text = request.decode('utf8')
        index = request_text.find('\r\n\r\n')
        req_line_headers = request_text[:index]
        headers_req_arr = req_line_headers.split('\r\n')
        self.line = headers_req_arr[0]
        self.headers = headers_req_arr[1:]
        self.body = request_text[index+4:]
        self.method = self.line.split(' ')[0]
        self.path = self.line.split(' ')[1]
        self.http_version = self.line.split(' ')[2]
        
