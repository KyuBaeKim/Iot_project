
from multiprocessing import parent_process 

# GPIO-ZERO
from gpiozero import PWMLED
from signal import pause

# CDS 모듈 설정
import spidev 
import time

# 시간 모듈 설정
import datetime
import time

# -*- coding: utf-8 -*- 
#---- subscriber.py  데이터 받기 
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish


from data_check import data_check
# CDS 변수

# 딜레이 시간(센서 측정 간격) 
delay = 0.5
# MCP3008 채널 중 센서에 연결한 채널 설정 
pot_channel = 0
# SPI 인스턴스 spi 생성 
spi = spidev.SpiDev()
# SPI 통신 시작하기 
spi.open(0, 0)
#SPI통신 속도 설정 
spi.max_speed_hz = 100000



led = PWMLED(14)
nw = datetime.datetime.now() # 현재 시간 설정

status = 0
test = "" 
LED_val = [0]
val_1 = [0,0,0,0,0,0,0]
val_2 = [0,0,0,0,0,0,0]
state = [0,0,0,0,0,0,0]


# CDS(조도센서) 값 읽기
#0~7 까지 8개의 채널에서 SPI 데이터 읽기 
def readadc(adcnum):
    if adcnum < 0 or adcnum > 7:
        return -1
    r = spi.xfer2([1, 8+adcnum <<4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

    


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

#서버로부터 publish message를 받을 때 호출되는 콜백
def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))
    
def on_message(client, userdata, msg):

    global val_1
    global val_2
    global LED_val
    global message

    print(str(msg.payload.decode("utf-8")))
    message = str(msg.payload.decode("utf-8"))
    
    state = data_check(LED_val,val_1, val_2, message)

    print(f"state = {state}")
 
    if ( state == [1,1,1,1,1,1,1]):
        val_2 = message.split(",")
    
    if( state == [2,2,2,2,2,2,2]):
        LED_val = message

    

    
    

    
try:
    client = mqtt.Client() #client 오브젝트 생성
    client.on_connect = on_connect #콜백설정
    client.on_subscribe = on_subscribe
    client.on_message = on_message #콜백설정

    client.connect('175.211.162.37', 1883)  # 라즈베리파이 커넥트  
    client.subscribe('Iot/LED', 0)  # 토픽 : temp/temp  | qos : 1
    client.publish('data',"init,mood")
    client.loop_start()
    
    



    
    while 1:

        try:    
                # readadc 함수로 pot_channel의 SPI 데이터를 읽기 
            pot_value = readadc(pot_channel)
            if(LED_val=="on"):
                led.value = 1
                print("LED ON")
                LED_val = ""

            elif(LED_val=="off"):
                led.value = 0
                print("LED OFF")
                LED_val = ""

                    
                  
            if (val_2[0] == "init_return")or(val_2[0]=="setting"):
                print(f"result1 = {val_2[0]}")
                if val_2[1] == "mood":

                    print(f"result2 = {val_2[1]}")
                    

                    # 첫 번째 설정 시간
                    select_hour1 = int(val_2[3])
                    select_minute1 = int(val_2[4])
                    select1 = select_hour1 * 60 + select_minute1

                    # 두 번째 설정 시간
                    select_hour2 = int(val_2[5])
                    select_minute2 = int(val_2[6])
                    select2 = select_hour2 * 60 + select_minute2

                    nw_time_hour = nw.hour
                    nw_time_minute = nw.minute
                    nw_time = nw_time_hour * 60 + nw_time_minute

                    if(val_2[2] == "1"):
                        print(f"result3 = {val_2[2]}")
                        
                        if(select2 > nw_time >= select1):  # (select2 > nw_time >= select1)
                                print(f"result3 = {val_2}")
                                if(pot_value >= 1000) :
                                    print(f"result4 = LED on ")
                                    led.value = 1 # full brightness 
                                elif(1000 > pot_value >= 900) :
                                    led.value = 0.5 # half brightness 
                                elif(960 > pot_value):
                                    led.value = 0 # full brightness 
                                print(pot_value)
                                
                                
                        elif(nw_time >= select2 ): #(nw_time >= select2 )
                                led.value = 0
                    elif(val_2[2]=="0"):
                            led.value = 0
                val_2 = [0,0,0,0,0,0,0]                
            time.sleep(3)

        except KeyboardInterrupt:
            print("bye!")
            exit()
        except:
            print("message error")
            time.sleep(1)
            pass

except KeyboardInterrupt:
    print("bye")