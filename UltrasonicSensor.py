#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import sys
def get_average_distance():
    GPIO.output(trigPin,0)
    time.sleep(0.2)
    GPIO.output(trigPin,1)
    time.sleep(0.2)
    GPIO.output(trigPin,0)
    while GPIO.input(echoPin)==0:
        pass
    echoStartTime=time.time()
    while GPIO.input(echoPin)==1:
        pass
    echoStopTime=time.time()
    waveTime=(echoStopTime-echoStartTime)/2
    distance=round(343000*waveTime,1)
    distancee=183-distance
    return distancee

def control_heating_wires(current_state):
    global previous_state
    if current_state==2:
        GPIO.output(wire1,1)
        GPIO.output(wire2,1)
        GPIO.output(heating_pin,1)
        print("Heating wire is turned on",flush=True)
    if current_state==1:
        if previous_state==2: # if the current snow is above top level, turn on the heating wires
            GPIO.output(wire1,1)
            GPIO.output(wire2,1)
            GPIO.output(heating_pin,1)
            print("Heating wire is turned on",flush=True)
        elif previous_state==0:
            GPIO.output(wire1,0) #if the current snow is between base level and top level, but was initially at base level, turn off the heating wires
            GPIO.output(wire2,0)
            GPIO.output(heating_pin,0)
            print("Heating wire is turned off",flush=True)
    if current_state==0:
        GPIO.output(wire1,0) #If the current snow is below base level, turn off the heating wires
        GPIO.output(wire2,0)
        GPIO.output(heating_pin,0)
        print("Heating wire is turned off",flush=True)
    previous_state=current_state

#Setting to BCM mode        
GPIO.setmode(GPIO.BCM)
#Two sensor pins
trigPin=21
echoPin=17
#Two relay pins
wire1=6
wire2=16
#Heating wire led pin
heating_pin=26
#setting the TRigger pin of the sensor as an output, and the reciever pin as an input
GPIO.setup(trigPin,GPIO.OUT)
GPIO.setup(echoPin,GPIO.IN)
#setting both relay pins to output pin
GPIO.setup(wire1,GPIO.OUT)
GPIO.setup(wire2,GPIO.OUT)
#setting the blue led to output
GPIO.setup(heating_pin,GPIO.OUT)

#setting both relay pins to 0 state
GPIO.output(wire1,0)
GPIO.output(wire2,0)
GPIO.output(heating_pin,0)
previous_state=0
current_state=0
lvl0=15 #Base level
lvl1=50 #TOp level
x=1 #Variable for counting the number of readings
average=0 #variable for calculating the average of the distance measured by the sensor
try:
    while True:
        for i in range(30): #FOr every 30 readings, calculate its average, and then judge it.
            average_distance=get_average_distance()
            time.sleep(0.1)
            average+=average_distance
        average_distance=average/30
        print("Reading",str(x)+":",round(average_distance,1),"milli-meters",flush=True) #Print the average distance after 30 readings
        if average_distance>lvl1:
            control_heating_wires(2)
        if average_distance<lvl0:
            control_heating_wires(0)
        if lvl0<=average_distance<=lvl1:
            control_heating_wires(1)
        x+=1
        average=0
except KeyboardInterrupt:
    GPIO.cleanup() #cleanup the GPIO pins when control+c is pressed
    print("GPIO is cleaned up")