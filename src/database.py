import pymysql
import sys,time
import logging
from threading import Lock

class DatabaseService(object):
    
    
    def __init__(self):
        self.connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='', db='gmjohnson')
        self.connection.autocommit(True)
        self.logger = logging.getLogger('database')
        self.create_tables()
        self.dblock = Lock()
        pass
        
    def create_tables(self):
        cursor = None
        try:
            self.logger.info("create database gmjohnson")
            cursor =self.connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS counter 
                (tagNum char(32) NOT NULL,
                timestamp BIGINT NOT NULL,
                counter1 BIGINT NOT NULL, 
                counter2 BIGINT NOT NULL, 
                counter3 BIGINT NOT NULL, 
                counter4 BIGINT NOT NULL, 
                generation1 BIGINT NOT NULL DEFAULT 0,
                generation2 BIGINT NOT NULL DEFAULT 0,
                generation3 BIGINT NOT NULL DEFAULT 0,
                generation4 BIGINT NOT NULL DEFAULT 0,
                reset1 BIGINT,
                reset2 BIGINT,
                reset3 BIGINT,
                reset4 BIGINT,
                resetTimestamp BIGINT,                
                PRIMARY KEY(tagNum))""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS history 
                (tagNum char(32) NOT NULL,
                timestamp BIGINT NOT NULL,
                counter1 BIGINT NOT NULL, 
                counter2 BIGINT NOT NULL, 
                counter3 BIGINT NOT NULL, 
                counter4 BIGINT NOT NULL, 
                generation1 BIGINT NOT NULL DEFAULT 0,
                generation2 BIGINT NOT NULL DEFAULT 0,
                generation3 BIGINT NOT NULL DEFAULT 0,
                generation4 BIGINT NOT NULL DEFAULT 0,
                reset1 BIGINT,
                reset2 BIGINT,
                reset3 BIGINT,
                reset4 BIGINT,
                resetTimestamp BIGINT,                
                PRIMARY KEY(tagNum))""")
        except:
            self.logger.error("error creating database: %s", sys.exc_info()[0])
            pass
        finally:
            cursor.close()
    '''insert or update counter based on tagNum and type'''
    def update_counters(self,tagNum,timestamp,counter1,counter2,counter3,counter4):
        with self.dblock:
            counters = self.get_tag_counters(tagNum)
            generation1,generation2,generation3,generation4 = 0,0,0,0
            if counters:
                if(counters[0]['counter1'] > counter1):
                    generation1 = counters[0]['generation1']+1
                if(counters[0]['counter2'] > counter2):
                    generation2 = counters[0]['generation2']+1
                if(counters[0]['counter3'] > counter3):
                    generation3 = counters[0]['generation3']+1
                if(counters[0]['counter4'] > counter4):
                    generation4 = counters[0]['generation4']+1
                    
            cmd = "INSERT INTO counter (tagNum,timestamp,counter1,counter2,counter3,counter4,\
                generation1,generation2,generation3,generation4,\
                reset1,reset2,reset3,reset4,resetTimestamp)\
                    VALUES (%s,%s,%s,%s,%s,%s,\
                            %s,%s,%s,%s,\
                            0,0,0,0,0)\
                    ON DUPLICATE KEY UPDATE\
                     timestamp=%s,\
                     counter1=%s,counter2=%s,counter3=%s,counter4=%s,\
                     generation1=%s,generation2=%s,generation3=%s,generation4=%s"
            cursor = None
            try:
                self.logger.info(cmd)
                self.connection.ping(reconnect=True)
                cursor = self.connection.cursor(pymysql.cursors.DictCursor)
                cursor.execute(cmd,(tagNum,timestamp,counter1,counter2,counter3,counter4\
                                    ,generation1,generation2,generation3,generation4,
                                    timestamp,counter1,counter2,counter3,counter4\
                                    ,generation1,generation2,generation3,generation4,))
            except:
                self.logger.error("error updating counter: %s", sys.exc_info()[0])
                pass
            finally:
                cursor.close()
    
    def reset_counters(self,tagNum,resetTimestamp=int(time.time())):
        with self.dblock:
            counter = self.get_tag_counters(tagNum)[0]
            result = self._reset_counters(tagNum, 
                                counter['counter1'],
                                counter['counter2'],
                                counter['counter3'],
                                counter['counter4'],
                                resetTimestamp)
            pass
        return result        
    def _reset_counters(self,tagNum,reset1,reset2,reset3,reset4,resetTimestamp):
        cursor = None
        result = None
        cmd = "UPDATE counter set reset1= %s,reset2=%s,reset3=%s,reset4=%s,\
            resetTimestamp=%s,generation1=0,generation2=0,generation3=0,generation4=0 where tagNum=%s"
        try:
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(cmd,(reset1,reset2,reset3,reset4,
                                    resetTimestamp,
                                    tagNum))
        except:
            pass
        finally:
            cursor.close()
        return result

    def _update_history(self,tagNum,counterA,counterB,counterC,counterD,
                        generationA,generationB,generationC,generationD,
                        resetA,resetB,resetC,resetD,resetTimestamp):
        cursor = None
        cmd = """INSERT INTO HISTORY(tagNum,counterA,counterB,counterC,counterD,
                generationA,generationB,generationC,generationD,
                resetA,resetB,resetC,resetD,resetTimestamp) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        try:
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(cmd,(tagNum,counterA,counterB,counterC,counterD,\
                                generationA,generationB,generationC,generationD,\
                                resetA,resetB,resetC,resetD,resetTimestamp))
        except:
            pass
        finally:
            cursor.close()
    def get_tag_counters(self,tagNum):
        cmd = "SELECT * from counter where tagNum = %s"
        cursor = None
        result = None
        try:
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(cmd,tagNum)
            result = cursor.fetchall()
        except:
            pass
        finally:
            cursor.close()
        return result
    
    def get_counters(self):
        cmd ="SELECT * from counter"
        cursor = None
        result = None
        try:
            self.connection.ping(reconnect=True)
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(cmd)
            result = cursor.fetchall()
        except:
            pass
        finally:
            cursor.close()
        return result
    
if __name__ == '__main__':
    database = DatabaseService()
    database.create_tables()
    print result