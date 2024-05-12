import time
import cv2 as cv  
import pathlib 
import paho.mqtt.client as mqtt
import statistics 
import sqlite3  
import datetime

class ThresholdDataBase: 
    def __init__(self, a_db_name, a_table_name):  
        self.db_name=a_db_name 
        self.table_name=a_table_name 
        self.connection = sqlite3.connect(self.db_name)  
        self.cursor = self.connection.cursor()

        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER AUTO_INCREMENT PRIMARY KEY, avg_person_count INTEGER)')
                
        self.close_db()
    
    def open_db(self): 
        self.connection = sqlite3.connect(self.db_name)  
        self.cursor = self.connection.cursor()  
    
    def close_db(self): 
        self.connection.commit() 
        self.cursor.close()
        self.connection.close()
       
    def write_threshold(self, avg_person_count): 
        self.open_db()  

        self.cursor.execute(f'INSERT INTO {self.table_name} (avg_person_count) VALUES ({avg_person_count})')

        self.close_db()

    def get_threshold(self, thresh_type):
        self.open_db  
        
        if(thresh_type=='max'):self.cursor.execute(f'SELECT * FROM {self.table_name} ORDER BY avg_person_count DESC LIMIT 1')  
        elif (thresh_type=='min'): self.cursor.execute(f'SELECT * FROM {self.table_name} ORDER BY avg_person_count ASC LIMIT 1')  
        
        row=self.cursor.fetchone() 
        
        self.close_db 

        return float(row['avg_person_count'])
    

class MQTTClient: 
    def __init__(self, a_broker_url="", a_broker_port=0, a_username="", a_password="",a_publish_rate=1): 
        
        self.publish_rate=a_publish_rate
        self.client = mqtt.Client()
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)  # Use secure TLS/SSL
        self.client.tls_insecure_set(False)
        self.client.username_pw_set(a_username, a_password)
        self.client.connect(a_broker_url, a_broker_port)
        self.client.loop_start()  


    def publish(self,topic,message): 
        print(f"published {message} on {topic}")
        self.client.publish(topic, message)  
        
    
    def __del__(self): 
        self.client.loop_stop() 
        self.client.disconnect()


class NonBlockingTimer:
    def __init__(self): 
        self._current_time=time.time()
        
    def nonBlock(self, logic, time_interval, **kwargs): 
        new_current_time=time.time()

        if new_current_time-self._current_time>time_interval:  
            logic(**kwargs) 
            self._current_time=new_current_time 


class AlgorithmObject: 
    def __init__(self, a_camera_no=0, a_capture_rate=2, a_cascade_file="", a_database=None): 
        self.cam=cv.VideoCapture(a_camera_no) 
        self.capture_rate=a_capture_rate 
        self.haar_cascade=cv.CascadeClassifier(str(pathlib.Path(__file__).resolve().parent)+'\\'+a_cascade_file) 
        self.database=a_database
        self.person_ct=[] 
       
    def capture_faces(self): 
        ret, frame =self.cam.read()  
        self.person_ct.append(len(self.haar_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=3)))  
        
        
        print(f'current person_avg: {self.person_ct[0]}')
        if(len(self.person_ct)>2):   
            moving_avg=statistics.mean(self.person_ct) 
            self.person_ct.clear()
            self.person_ct.append(moving_avg) 
            
    
    def write_thresh_to_db(self):  
        if(self.database is not None):
            self.database.write_threshold(avg_person_count=self.person_ct[0]) 
            print(f'successfully wrote {self.person_ct[0]} to {self.database.db_name} in table {self.database.table_name}')
            self.person_ct.clear
            self.person_ct[0]=0   
            

    def calculate_risk(self): 
        max_person_ct=self.database.get_threshold('max') 
        min_person_ct=self.database.get_threshold('min') 

        risk_lvl=round((self.person_ct/(max_person_ct-min_person_ct))*10) 
        self.person_ct.clear
        self.person_ct[0]=0  

        return risk_lvl

    def print_faces(self): 
        print(self.person_ct)
        

myNBT=NonBlockingTimer()  
myNBT2=NonBlockingTimer() 
myNBT3=NonBlockingTimer()
myNBT4=NonBlockingTimer()
myThresholdDB=ThresholdDataBase ( 
                                a_db_name="threshold.db",
                                a_table_name="thresholds"
                                )

myAO=AlgorithmObject            (
                                a_capture_rate=5, 
                                a_cascade_file="haar_face.xml", 
                                )

myAOThreshold=AlgorithmObject   (
                                a_capture_rate=5, 
                                a_cascade_file="haarcascade_fullbody.xml",
                                a_database=myThresholdDB, 
                                ) 


myMQ=MQTTClient                 (
                                a_broker_url="a98bdda5eadc4d9db9ad2f32aceb4ae4.s1.eu.hivemq.cloud",  
                                a_broker_port=8883, 
                                a_username= "hivemq.webclient.1714355997131", 
                                a_password="D:k.0tg9@a53bJCB!uMO",  
                                a_publish_rate=5
                                )

while True:  
    #myNBT.nonBlock(logic=myAO.capture_faces, time_interval=myAO.capture_rate) 

    myNBT3.nonBlock(logic=myAOThreshold.capture_faces,time_interval=myAOThreshold.capture_rate)
    
    myNBT4.nonBlock(logic=myAOThreshold.write_thresh_to_db, time_interval=60)

    #myNBT2.nonBlock(logic=myMQ.publish, time_interval=myMQ.publish_rate, topic="test/topic", message=myAO.person_ct[0])
    


    