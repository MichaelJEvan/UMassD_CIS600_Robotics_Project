
'''
############################################################
#
#   Michael Evan
#   University of Massachusetts Dartmouth
#   Graduate Department of Computer Science
#   CIS600 Masters Project Spring 2025
#
#   sensor distance data script
#
#   Final script write: use this script for project
#
#   Function version for call in seperate programs
#
############################################################
'''

import RPi.GPIO as GPIO
import time

# Set the GPIO mode (BCM on BOARD)
GPIO.setmode(GPIO.BCM)

# GPIO Pin config
TRIG_L = 13  # Left sensor trigger
ECHO_L = 16  # Left sensor echo
TRIG_C = 6   # Center sensor trigger
ECHO_C = 20  # Center sensor echo
TRIG_R = 5   # Right sensor trigger
ECHO_R = 21  # Right sensor echo

# Setup GPIO
GPIO.setup(TRIG_L, GPIO.OUT)
GPIO.setup(ECHO_L, GPIO.IN)
GPIO.setup(TRIG_C, GPIO.OUT)
GPIO.setup(ECHO_C, GPIO.IN)
GPIO.setup(TRIG_R, GPIO.OUT)
GPIO.setup(ECHO_R, GPIO.IN)

def measure_distance(trig_pin, echo_pin):
    # Trigger the sensor
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.01)  # Trigger for 10ms
    GPIO.output(trig_pin, GPIO.LOW)

    # Wait for echo to start
    while GPIO.input(echo_pin) == 0:
        pulse_start = time.time()

    # Wait for echo to end
    while GPIO.input(echo_pin) == 1:
        pulse_end = time.time()

    # Calculate duration and distance
    pulse_duration = pulse_end - pulse_start

    # speed if sound calculation with conversion to millimeters
    distance = ((pulse_duration * 34300) / 2) * 10  # Distance in mm

    return distance

def read_sensor_data():
    # Measure distances
    # function call to measure sensor distance
    # time.sleep() delay to avoid cross-talk
    distance_L = measure_distance(TRIG_L, ECHO_L)
    time.sleep(0.1)
    distance_C = measure_distance(TRIG_C, ECHO_C)
    time.sleep(0.1)
    distance_R = measure_distance(TRIG_R, ECHO_R)
    time.sleep(0.1)

    return{
        'distance_L': distance_L,
        'distance_C': distance_C,
        'distance_R': distance_R
    }
