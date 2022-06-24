from machine import UART
import machine
import _thread
import time
from machine import ADC,Pin
import re

## Hyperparameters
#  Configure Network 
uart = UART(0,115200) # uart on uart1 with baud of 115200
wifi_ssid = ("TOTOLINK_N200RE")
wifi_password = ("raspberry")

#  Configure LED PIN
led = Pin(25, Pin.OUT)

# Global Variable
query = None
lamp = False

# Set up an analog input on ADC0 (GP26), which is physically pin 31.
sensor = ADC(Pin(26))

def connectNetwork(toggle_connect):
    print ("Conencting to Wireless")
#     Connect to wifi, this only needs to run once, ESP will retain the CWMODE and wifi details and reconnect after power cycle, leave commented out unless this has been run once.
    if(toggle_connect == True):
        print (" - Setting AP Mode...")
        uart.write('AT+CWMODE=1'+'\r\n')
        time.sleep(2)
        print (" - Connecting to WiFi...")
        uart.write('AT+CWJAP="'+wifi_ssid+'","'+wifi_password+'"'+'\r\n')
        time.sleep(2)
    else:
        print (" - Already Connected...")
        
    print (" - Setting Connection Mode...")
    uart.write('AT+CIPMUX=1'+'\r\n')
    time.sleep(2)
    print (" - Getting IP ...")
    uart.write('AT+CIFSR'+'\r\n')
    query = uart.read().decode("utf-8")
    ip_addr = str.split(query,"\r")[6]
    ip_addr = str.split(ip_addr,",")[1]
    ip_addr = str.replace(ip_addr,'"','')
    mac_addr =  re.match("^.*\"(.*)\".*$",query).group(1)
    return ip_addr,mac_addr
    
def testNetwork(address):
    print (f" - Pinging {address}")
    uart.write(f'AT+PING={address}'+'\r\n')
    print(uart.read())
    
def main():
    global query,uart,sensor,lamp
    ip_addr,mac_addr = connectNetwork(False)
    print (f" => Found {ip_addr} \n => Found {mac_addr}")
    while True:
        # Lampu
        if(lamp == True):
            led.value(1)
            time.sleep(1)
            led.value(0)
            time.sleep(1)
        # Ambil Pengukuran
        measurement = sensor.read_u16()
        # Konversi ADC ke Voltase 5V
        voltage = measurement*5/65536
        # Konversi Voltase ke pH
        ph = 7+((2.5-voltage)/0.18)
        print(measurement,voltage,ph)
        time.sleep(1)
        

if __name__ == "__main__":
    main()