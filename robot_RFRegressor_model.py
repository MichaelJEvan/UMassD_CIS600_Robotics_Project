#########################################################################
#
#   Michael J Evan
#   University of Massachusetts Dartmouth
#   Graduate Department of Computer Science
#   CIS-600 Masters Computer Science Project Spring 2025
#   
#   AUTONOMOUS NAVIGATION CODE
#
#   Autonomous Robot on the Raspberry Pi 5 8G RAM platform
#   utilizing machine learning algorithm for autonomous robot movement
#   inside a closed track
#
#   Note: **** must include sensor_readings.py in directory to work ***
#
#   Note: Upper Left PS5 button (4) to abort program
#
#   Auto-throttle is engaged... multiple statements need un-commenting
#   includeding DEAD ZONE check to revert back to manual throttle
#
#########################################################################

import csv  # for ML algorithm training data
import pygame  # interface PS5 game controller
from gpiozero import PWMOutputDevice  # motor control
import time
from time import sleep
import pickle  # for loading the pickle model
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# (separate file) for reading the sensor data
from sensor_readings import read_sensor_data

# Load Random Forest Regressor model from .pkl file
with open('/home/me/Desktop/robot_rf_regressor_model.pkl', 'rb') as model_file:
    rf_model = pickle.load(model_file)
    print()
    print("**** Robot Model Loaded .......")

# force CSV file save location
csv_file_path = '/home/me/Desktop/robots_RFRegressor_data.csv'

# Variables: distance, throttle & direction 
distance_L = 250.00  # initial default value for left distance
distance_C = 0.0
distance_R = 0.0
throttle = 0.00

# feel_the_need_for_speed = 1.0     # full speed
# feel_the_need_for_speed = 0.75    # 3/4 speed
# feel_the_need_for_speed = 0.5       # 1/2 speed
feel_the_need_for_speed_L = 0.38   # 40% speed ... actually R motor speed
feel_the_need_for_speed_R = 0.44

# Dead zone threshold
DEAD_ZONE = 0.0  # setting to 0.0 to test control without it 

# Initialize Pygame
pygame.init()

# Set up the motor PWM pins
motor_left_forward = PWMOutputDevice(17)
motor_left_backward = PWMOutputDevice(18)
motor_right_forward = PWMOutputDevice(22)
motor_right_backward = PWMOutputDevice(23)

# Set up motor enable pins
left_motor_enable = PWMOutputDevice(24)
right_motor_enable = PWMOutputDevice(25)

def emergency_stop():
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 4:  # PS5 Button 4 (left upper button) press = Emergency Abort
                stop_motors()
                print('********************* WARNING - ROBOT - USER - EMERGENCY - ABORT *****************')
                pygame.quit()
                exit()

def stop_motors():
    motor_left_forward.value = 0
    motor_left_backward.value = 0
    motor_right_forward.value = 0
    motor_right_backward.value = 0
    left_motor_enable.off()
    right_motor_enable.off()

def distance_filter(current_distance, previous_distance):
    max_course_value = 1800.000  # max straight length in mm
    if current_distance >= max_course_value:
        current_distance = previous_distance
    return current_distance

def write_robot_csv_file(writer):
    time_stamp = time.time()
    writer.writerow({
        'timestamp': time_stamp,
        'joystick_throttle': throttle,
        'joystick_direction': direction,
        'distance_L': distance_L,
        'distance_C': distance_C,
        'distance_R': distance_R,
    })

def print_distances():
    print()
    print('*************************************************************')
    print(f"Distance to Left sensor: {distance_L:.2f} mm")
    print(f"Distance to Center sensor: {distance_C:.2f} mm")
    print(f"Distance to Right sensor: {distance_R:.2f} mm")

def auto_throttle(throttle):
    # provides automatic smooth full throttle
    # -1 = full-throttle
    if throttle != -1:
        print('throttle = ', throttle)
        throttle += -.10    # advances throttle
    return throttle

# Enable the motors at the start
left_motor_enable.value = 1
right_motor_enable.value = 1

# Initialize CSV file writing
with open(csv_file_path, mode='w', newline='') as csv_file:
    fieldnames = ['timestamp', 'joystick_throttle', 'joystick_direction', 'distance_L', 'distance_C', 'distance_R']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Main control loop
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # Handle emergency stop
            emergency_stop()

            # Prepare input data for the model
            features = np.array([[distance_L, distance_C, distance_R]])  # Ensure proper shape
            # Predict the joystick direction using the Random Forest model
            direction = rf_model.predict(features)[0]  # Get the predicted direction

            # auto-throttle up to max -1
            throttle = auto_throttle(throttle)

            # Compute motor speeds based on predicted direction and throttle
            left_speed = (-throttle - direction) * feel_the_need_for_speed_L
            right_speed = (-throttle + direction) * feel_the_need_for_speed_R

            # Limit the speed values to the range of 0 to 1
            left_speed = max(0, min(1, left_speed))
            right_speed = max(0, min(1, right_speed))

            # Control the left motor
            if left_speed > 0:
                motor_left_forward.value = left_speed
                motor_left_backward.value = 0
            else:
                motor_left_forward.value = 0
                motor_left_backward.value = -left_speed

            # Control the right motor
            if right_speed > 0:
                motor_right_forward.value = right_speed
                motor_right_backward.value = 0
            else:
                motor_right_forward.value = 0
                motor_right_backward.value = -right_speed

            previous_distance_L = distance_L
            previous_distance_C = distance_C
            previous_distance_R= distance_R

            if pygame.time.get_ticks() % 250 < 100:  # Every 250 ms
                distances = read_sensor_data()  # read via function in sensor_raedings.py script
                distance_L = distances['distance_L']
                distance_C = distances['distance_C']
                distance_R = distances['distance_R']
                

                # checks for out of bounds erroneous data ...
                distance_L = distance_filter(distance_L, previous_distance_L)
                distance_C = distance_filter(distance_C, previous_distance_C)
                distance_R = distance_filter(distance_R, previous_distance_R)

                # final distance, throttle, direction readings round to 2 decimal places
                distance_L = round(distance_L,2)
                distance_C = round(distance_C,2)
                distance_R = round(distance_R,2)
                throttle = round(throttle,2)
                direction = round(direction,2)

            # uncomment below to:  Write distance and control data to CSV
            write_robot_csv_file(writer)

            # Display sensor distances to terminal
            print_distances()

            # Sleep briefly to reduce CPU load
            sleep(0.1)

    except KeyboardInterrupt:   
        pass

    finally:
        # Power down the robot program
        stop_motors()
        pygame.quit()
