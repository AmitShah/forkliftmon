'''
Created on Aug 8, 2013

@author: amitshah
'''
from mailgun import *
from bluerover import Api
from database import DatabaseService
import ssl,socket,sys
import os,tornado
from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler
import sys,functools,json
from threading import Lock
import datetime,logging, threading

logger = logging.getLogger('sensor_main')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('sensor.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)


'''helper method to handle casting of improper chars'''
def ignore_exception(IgnoreException=Exception,DefaultVal=None):
    """ Decorator for ignoring exception from a function
    e.g.   @ignore_exception(DivideByZero)
    e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
    """
    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal
        return _dec
    return dec

sint = ignore_exception(IgnoreException=ValueError)(int)
class Decoder(object):
    def __init__(self,name,start,end,callback):
        self.name = name
        self.start =start
        self.end = end
        self.callback = callback

def hex_to_int(hex_data):
    return int(hex_data,16)    
class CounterRecorder(object):
    
    def __init__(self,database):
        self.database = database
        self.decoder = [Decoder('timestamp',10,18,hex_to_int),
                        Decoder('counter1',30,34,hex_to_int), 
                        Decoder('counter2',26, 30,hex_to_int), 
                        Decoder('counter3',22, 26,hex_to_int),
                        Decoder('counter4',18, 22,hex_to_int),
                        ]
        pass
    def _decode(self,raw):
        temp = raw
        result ={}
        for d in self.decoder:
            data = temp[d.start:d.end]
            if (d.callback):
                data = d.callback(data)
            result[d.name] = data
        return result
    
    def notify(self, message):
        try:
            event = json.loads(message)        
            if isinstance(event,dict) and 'rfidTagNum' in event:
                tagNum = event['rfidTagNum']
                decoded_packet = self._decode(event['rawData'])
                logger.info("decoded data:%s",event['rawData'])
                self.database.update_counters(tagNum,\
                                              decoded_packet['timestamp'],\
                                              counter1=decoded_packet['counter1'],\
                                              counter2=decoded_packet['counter2'],\
                                              counter3=decoded_packet['counter3'],\
                                              counter4=decoded_packet['counter4'])
                pass
        except:
            logger.error("error on notify:%s", sys.exc_info()[0])            
            pass
    

def update_listeners(counters):
    for h in UpdateHandler.handlers:
        h(message=counters)    
    pass
     
'''Look for new line characters and notify all observer per line '''
class LineObserver(CounterRecorder):
    def __init__(self,database):
        CounterRecorder.__init__(self,database)
        self.buffer = ''
        
    '''we need to protect buffer from async calls :('''        
    def notify(self,message):
        try:              
            #prevent multiple async calls from overriding the buffer while in processing  
            self.buffer= self.buffer+message                
            while "\n" in self.buffer:
                (line, self.buffer) = self.buffer.split("\n", 1)
                data = line.strip() #remove blank lines (when keep alive is sent from server)
                if data:
                    logger.info(('processing buffered data:%s' % self.buffer))
                    CounterRecorder.notify(self, data)  
                    #trigger all clients to update                    
                    counters = self.database.get_counters()
                    update_listeners(counters)
        except:
            logger.error('notify exception')
            pass
        finally:
            pass
        

class UpdateHandler(WebSocketHandler):
    
    handlers = []
   
    def initialize(self,api,database):
        self.api = api
        self.database = database
        pass
    
    def open(self):
        UpdateHandler.handlers.append(self)
        counters = self.database.get_counters()
        self(counters)
        
    def on_message(self, message):
        cmd = json.loads(message)
        pass
    
    def on_close(self):
        UpdateHandler.handlers.remove(self)
        
    def broadcast_as_json(self,message):
        try:
            data = json.dumps(message)
            self.write_message(data)
        except:
            pass
        
    def __call__(self,message=None): 
        if message:       
            self.broadcast_as_json(message)
     
    
    
class BaseHandler(tornado.web.RequestHandler):        
    def initialize(self,api,database):
        self.api = api
        self.database = database
        pass
    
    def get_current_user(self):
        '''used for web api administration access'''
        #self.account_service.getUserWithPassword()
        user = self.get_secure_cookie('user')
        if user is not None:            
            user = json.loads(self.get_secure_cookie("user"))
        return user

class LoginHandler(BaseHandler):
    
    def get(self):
        self.render('login.html',message=None)
        
    def post(self):
        username = self.get_argument('username', True)
        password = self.get_argument('password',True)
        user = {'username':username}
        try:
            if user is not None:            
                self.set_secure_cookie("user",json.dumps(user))
                self.redirect(self.get_argument("next", u"/"))
        except:
            self.render('login.html',message='please try again.\
            If you continue to experience issues, please contact support')
        
class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/login")


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('home.html')

class AuditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('audit.html')
    
class RfidsHandler(BaseHandler):    
    def post(self):
        json_rfid= self.api.call_api("/rfid", {})
        self.write(json_rfid)          

class DevicesHandler(BaseHandler):
    def post(self):
        devices = self.api.call_api("/device",{})
        self.write(devices)
        
from tornado.escape import json_encode
from threading import Lock

class ResetHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,id):
        flag = self.database.reset_counters(id)
        #update all listeners
        counters = self.database.get_counters()    
        update_listeners(counters)
        
if __name__ == '__main__':
    
    '''let setup tcp connection to the upstream service to get sensor data 
    and handle this data with a async socket read for distribution :) '''
    #demoaccount
    api = Api(token='71pbUIoDvzq4XD+8NslFqaYrmdRxFljvNsTJi+XA',
              key='X4+tfKOhKZz4x41a+UsoHBfliC26sJmijI+RqpQO8SXB6Z4iv3wzk291+I4/HJPg',
              base_url='https://developers.polairus.com')
    
    database= DatabaseService()
    observer= LineObserver(database)
    
    sock = socket.socket()    
    s = ssl.wrap_socket(sock)
    
    def connect_to_service():        
        s.connect(('developers.polairus.com',443))    
        s.sendall(api.create_eventstream_request())
        pass
    
    
    def data_handler(sock,fd,events):
        try:                    
            data = sock.recv(4096)
            logger.info(('received data:%s' % data))
            observer.notify(data)        
        except:
            logger.error('data handler')
            sock.close()
            ioloop = tornado.ioloop.IOLoop.instance()
            ioloop.remove_handler(fd)
            ioloop.add_timeout(datetime.timedelta(seconds=60), connect_to_service) 
        pass


    callback = functools.partial(data_handler, s)
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_handler(s.fileno(), callback, ioloop.READ)    
    ioloop.add_callback(connect_to_service)
        
    #define all the services
    services = dict(
        api = api,
        database = database
        )
    
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        cookie_secret= 'secret_key',
        login_url='/login'
        )
      
    application = tornado.web.Application([
    (r"/update", UpdateHandler,services),    
    (r"/audit", AuditHandler, services),
    (r"/reset/(\d+)", ResetHandler, services),
    (r"/login", LoginHandler, services),
    (r"/logout", LogoutHandler, services),
    (r"/*", MainHandler,services),
          
    ], **settings)
    
    sockets = tornado.netutil.bind_sockets(9999)
    server = HTTPServer(application)
    server.add_sockets(sockets)
    
    #pc.start()
    ioloop.start()
    
