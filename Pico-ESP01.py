from machine import UART
from machine import ADC,Pin
from esp8266 import ESP8266
import machine
import _thread
import time
import re
import sys
import random

## -- Hyperparameters -- #

# - Configure LED PIN - #
led = Pin(25, Pin.OUT)
# - Configure ADC0 (GP26), which is physically pin 31. - #
sensor = ADC(Pin(26))


# - Configure Network - #
uart = UART(0,115200)
wifi_ssid = ("TOTOLINK_N200RE")
wifi_passwd = ("raspberry")
server_ip = "192.168.0.183"

# - Configure ESP8266 - #
esp01 = ESP8266()
esp8266_at_ver = None

# - Global Variable - #
query = None
lamp = False
id = 1
hash = "None"

## -- Functions -- ##
def doBlink():
    led.value(1)
    time.sleep(1)
    led.value(0)
    time.sleep(1)
    
def main():
    ## -- Boot Beep -- ##
    doBlink()
    ## -- Global Variables -- ##
    global query,uart,sensor,lamp,id,hash
    ## -- Welcome Print -- ##
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("RPi-Pico MicroPython Ver:", sys.version)
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    ## -- Activate ESP-01 -- ##
    result = esp01.startUP()
    if(result == True):
        doBlink()
        print("ESP-01 - StartUP : ",result)
        
        result = esp01.echoING()
        if(result == True):
            doBlink()
            print("ESP-01 - Echo-Off : ",result)
        else:
            print("ESP-01 - Echo-On")
        result = esp01.setCurrentWiFiMode()
        if(result == True):
            doBlink()
            print("ESP-01 - WiFi Mode : ",result)
        else:
            print("WiFi Mode Failed")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        esp8266_at_ver = esp01.getVersion()
        if(esp8266_at_ver != None):
            print("ESP-01 - Version : ",esp8266_at_ver)
        else:
            print("ESP-01 might not connected properly")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("ESP-01 tries to connect with the WiFi")
        while (1):
            if "WIFI CONNECTED" in esp01.connectWiFi(wifi_ssid,wifi_passwd):
                print("ESP-01 connected with the WiFi")
                doBlink()
                break;
            else:
                print(".")
                time.sleep(2)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        
        first = True
        
        while (True):
            ## -- Fetch Sensor Data -- ##
            sample_voltage = 0
            for i in range(0,5):
                sensor_value = sensor.read_u16()
                sample_voltage += ((5/65535)*sensor_value)
                time.sleep(1)
            average_voltage = (sample_voltage/5)-1.75
            ph = 7+((2.58-average_voltage)/0.18)
            
            ## -- Generate Hash and Previous
            if(first == True):
                previous = "None"
            else:
                previous = hash
            
            hash = str(random.random())
            hash = str.split(hash,".")[1]
            
            
            ## -- Value Control -- ##
            # print(sensor_value,average_voltage,ph,previous,hash)
            
            ## -- Query Update -- ##
            uri = f"/DataReceiver.php?ph={ph}&volt={average_voltage}&previous={previous}&hash={hash}"
            print("Sending Query")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            httpCode, httpRes = esp01.doHttpGet(server_ip,uri,"RaspberryPi-Pico", port=8000)
            print(f"------------- {server_ip}{uri} Get Operation Result -----------------------")
            print("HTTP Code:",httpCode)
            print("HTTP Response:",httpRes)
            print("-----------------------------------------------------------------------------\r\n\r\n")
            doBlink()
            first = False
        else:
            print("UART Link Failed, Re-seat the pins")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

if __name__ == "__main__":
    while(True):
        try:
            main()
        except:
            print("Interruption Occured")
            continue
        break