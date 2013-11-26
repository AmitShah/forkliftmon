"""
BlueRover Web API Python

This simple class has two functions: to generate authentication tokens and to make requests to the API with the auth header.
"""

import urlparse
import hmac
import urllib
import urllib2
import binascii
import hashlib
import socket
import ssl

class Api(object):
    
    def __init__(self, key=None, token=None, base_url = "http://developers.polairus.com"):
        self._base_url = base_url
        self.set_credentials(key, token)
        
    def set_credentials(self, key, token):
        # Make sure that the key and key are passed in 
        if (key is None) or (token is None):
            raise Exception ("A consumer key and consumer key must be used for authentication.")
        
        self._key = key
        self._token = token
        
    def clear_credentials(self):
        self._key        = None
        self._token     = None
        
    def set_base_url(self, base_url):
        self._base_url = base_url;

    def call_api(self, relative_url, params, post_data = False):
        """
        Calls the BlueRover API for a specified endpoint.
        
        relative_url: The URL relative to the Base URL (default = developers.polairus.com/{{relative_url}})
        params: A dictionary of parameters
        post_data: Whether or not the data should be POSTed (boolean value)
        
        Returns a String containing the content of the response
        """
        
        # POST is not supported yet, so make sure all requests are GET
        post_data = False
        
        parameters = {}
                
        # Check to see if the params are empty
        if not params is None:
            parameters.update(params)
        
        # Set the URL
        url  = self._base_url + relative_url
        
        # Set the HTTP method
        if post_data:
            http_method = "POST"
        else:
            http_method = "GET"
            
        signature = self._generate_signature(self._key, http_method, url, parameters)
        endpoint_url = url
        if not post_data:
            # If there are parameters, add it to the end of the endpoint
            if len(parameters) > 0:
                endpoint_url = endpoint_url + "?"
                joined_params = []
                for k, v in parameters.items():
                    joined_params.append("%s=%s" % (k, v))
                joined_params = "&".join(joined_params)
                endpoint_url += joined_params        
    
            
            request = urllib2.Request(endpoint_url)
            # Add the authorization header
            request.add_header("Authorization", "BR " + self._token + ":" + signature)
            print signature
            print endpoint_url
            response = urllib2.urlopen(request)
            return response.read()
        else:
            raise Exception("POST not supported yet.")
        
    def _generate_signature(self, key, method, url, parameters = {}):
        parts = urlparse.urlparse(url)
        scheme, netloc, path = parts[:3]
        normalized_url = scheme.lower() + "://" + netloc.lower() + path
        
        base_elems = []
        base_elems.append(method.upper())
        base_elems.append(normalized_url)
        base_elems.append("&".join("%s=%s" % (k, self.__oauth_escape(str(v)))
                                  for k, v in sorted(parameters.items())))
        base_string = "&".join(self.__oauth_escape(e) for e in base_elems)
        return self.__get_message_signature(key, base_string)
        
    def __oauth_escape(self, val):
        if isinstance(val, unicode):
            val = val.encode("utf-8")
        return urllib.quote(val, safe="~")
        
    def __get_message_signature(self, key, message):
        return binascii.b2a_base64(hmac.new(key, message, hashlib.sha1).digest())[:-1]
    
    def get_events(self,start,end,page):
        result = self.call_api('/event', {'end_time':end,'start_time':start,'page':page})
        return result
    
    def get_devices(self):
        result = self.api.call_api("/device", {})
        return result
    
    def get_rfids(self):
        result = self.api.call_api("/rfid", {})
        return result
    
    def create_eventstream_request(self, host="https://developers.polairus.com/eventstream"):
        
        signature = self._generate_signature(self._key, "GET", host)       
        CRLF = '\r\n'
        request = [
               'GET /eventstream HTTP/1.1',
               'User-Agent: curl/7.21.3 (i686-pc-linux-gnu) libcurl/7.21.3 OpenSSL/0.9.8o zlib/1.2.3.4 libidn/1.18',
               'Host: developers.polairus.com',
               'Accept: */*',
               'Authorization:BR %(token)s:%(signature)s' %{'token':self._token, 'signature':signature},
               '',
               '',
               ]
        return CRLF.join(request)
    
    
    