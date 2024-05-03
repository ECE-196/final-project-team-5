import time
import cv2 as cv  
import pathlib 
import paho.mqtt.client as mqtt
    
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
    def __init__(self, a_camera_no=0, a_capture_rate=2, a_cascade_file=""): 
        self.cam=cv.VideoCapture(a_camera_no) 
        self.capture_rate=a_capture_rate 
        self.haar_cascade=cv.CascadeClassifier(str(pathlib.Path(__file__).resolve().parent)+'\\'+a_cascade_file) 
        self.person_ct=0 
        
    def capture_faces(self): 
        ret, frame =self.cam.read() 
        self.person_ct+=len(self.haar_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=3)) 

    def print_faces(self): 
        print(self.person_ct)
        

myNBT=NonBlockingTimer()  
myNBT2=NonBlockingTimer() 

myAO=AlgorithmObject(
                     a_capture_rate=2, 
                     a_cascade_file="haar_face.xml"
                    )

myMQ=MQTTClient     (
                     a_broker_url="a98bdda5eadc4d9db9ad2f32aceb4ae4.s1.eu.hivemq.cloud",  
                     a_broker_port=8883, 
                     a_username= "hivemq.webclient.1714355997131", 
                     a_password="D:k.0tg9@a53bJCB!uMO",  
                     a_publish_rate=5
                    )

while True:  
    myNBT.nonBlock(logic=myAO.capture_faces, time_interval=myAO.person_ct) 

    myNBT2.nonBlock(logic=myMQ.publish, time_interval=myMQ.publish_rate, topic="test/topic", message=myAO.person_ct)
    


    