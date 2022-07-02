from machine import UART
from machine import ADC,Pin
import machine
import _thread
import time
from esp8266 import ESP8266
import re

## -- Hyperparameters -- #

# - Configure LED PIN - #
led = Pin(25, Pin.OUT)
# - Configure ADC0 (GP26), which is physically pin 31. - #
sensor = ADC(Pin(26))


# - Configure Network - #
uart = UART(0,115200)
wifi_ssid = ("TOTOLINK_N200RE")
wifi_password = ("raspberry")
server_ip = "192.168.0.108"

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

def connectNetwork(toggle_connect):
    ip_addr,mac_addr = None, None
    print ("Connecting to Wireless")
    # Connect to wifi, this only needs to run once, ESP will retain the CWMODE and wifi details and reconnect after power cycle, leave commented out unless this has been run once.
    if(toggle_connect == True):
        print (" - Setting AP Mode ...")
        uart.write('AT+CWMODE=1'+'\r\n')
        time.sleep(5)
        print (" - Connecting to WiFi ...")
        uart.write('AT+CWJAP="'+wifi_ssid+'","'+wifi_password+'"'+'\r\n')
        time.sleep(15)
    
    # Do The Rest
    print (" - Setting Connection Mode ...")
    uart.write('AT+CIPMUX=1'+'\r\n')
    time.sleep(5)
    result = uart.read()
    if "OK" in result:
        print (" -> Success ")
        print (" - Getting IP ...")
        uart.write('AT+CIFSR'+'\r\n')
        time.sleep(5)
        result = uart.read()
        if "OK" in result:
            print (" -> Success ")
            # Preprocess UART Result
            result = result.replace(b"\r\n",b"")
            result = result.decode()
            # Get IP Addr
            ip_addr = str.split(result,",")[1]
            ip_addr = str.split(ip_addr,"+")[0]
            ip_addr = str.replace(ip_addr,'"','')
            # Get MAC Addr
            mac_addr =  re.match("^.*\"(.*)\".*$",result).group(1)
        else:
            print (" - Failed")
    else:
         print (" - Failed")
    return ip_addr,mac_addr
    
def testNetwork(address):
    print (f" - Pinging {address}")
    uart.write(f'AT+PING={address}'+'\r\n')
    print(uart.read())
    
def uploadData(ip_addr,mac_addr,measurement,voltage,ph):
    previous = hash
    uart.write('AT+CIPSTART=0,"TCP","192.168.0.184",8000'+'\r\n')
    print(uart.read())
    uart.write('AT+CIPCLOSE'+'\r\n')
    print(uart.read())
    
def main():
    global query,uart,sensor,lamp,id,hash
    ip_addr,mac_addr = connectNetwork(False)
    if(ip_addr is not None and mac_addr is not None):
        # IP Found, Do The Rest
        doBlink()
        print ("Parsing Result ...")
        print (f" -> Found {ip_addr} \n -> Found {mac_addr}")
        #     print (" - Connecting to Server...")
# #     uart.write('AT+CIPSTART=0,"TCP","192.168.0.184",8000'+'\r\n')
#     time.sleep(2)
#     while True:
#         # Lampu
#         if(lamp == True):
#             led.value(1)
#             time.sleep(1)
#             led.value(0)
#             time.sleep(1)
#         # Ambil Pengukuran
#         measurement = sensor.read_u16()
#         # Konversi ADC ke Voltase 5V
#         voltage = measurement*(5/65536)
#         # Konversi Voltase ke pH
#         ph = 7+((2.5-voltage)/0.18)
#         # print(measurement,voltage,ph)
#         uploadData(ip_addr,mac_addr,measurement,voltage,ph)
#         # Send Data
#         time.sleep(1)
    else:
        print ("Failed to Connect")
        

if __name__ == "__main__":
    main()