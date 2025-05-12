#########################################################################
#
#   Michael J Evan
#   University of Massachusetts Dartmouth
#   Graduate Department of Computer Science
#   CIS-600 Masters Computer Science Project Spring 2025
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

import csv # for ML algorithm training data
import pygame   # interface PS5 game controller
from gpiozero import PWMOutputDevice    # motor control
import time
from time import sleep

# (separate file) for reading the sesor data 
from sensor_readings import read_sensor_data

# force CSV file save location
csv_file_path = '/home/me/Desktop/robot_data.csv'

# Variables: distance, throttle & direction 
# initialized to float
distance_L = 0.0
distance_C = 0.0
distance_R = 0.0
direction = 0.0
throttle = 0.00

# joystick axis
LEFT_JOYSTICK_Y = 1  # Throttle
RIGHT_JOYSTICK_X = 3  # Direction

''' Speed factor to control overall max speed (0.0 to 1.0 for full speed)
    uncomment max speed choice  '''
# feel_the_need_for_speed = 1.0     # full speed
# feel_the_need_for_speed = 0.75    # 3/4 speed
# feel_the_need_for_speed = 0.5       # 1/2 speed
feel_the_need_for_speed = 0.4   # 40% seems optimal for controlling thru course

# Dead zone threshold
DEAD_ZONE = 0.2

# Initialize Pygame
pygame.init()

# Initialize joysticks
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Set up the motor PWM pins
motor_left_forward = PWMOutputDevice(17)
motor_left_backward = PWMOutputDevice(18)
motor_right_forward = PWMOutputDevice(22)
motor_right_backward = PWMOutputDevice(23)

# Set up motor enable pins
left_motor_enable = PWMOutputDevice(24)
right_motor_enable = PWMOutputDevice(25)

def emergency_stop():
    # PS5 Button 4 (left upper button) press = Emergency Abort
    if event.type == pygame.JOYBUTTONDOWN:
            print(f"Button {event.button} pressed")
            if event.button == 4:
                motor_left_forward.value = 0
                motor_left_backward.value = 0
                motor_right_forward.value = 0
                motor_right_backward.value = 0
                left_motor_enable.off()
                right_motor_enable.off()
                print()
                print('********************* WARNING - ROBOT - USER - EMERGENCY - ABORT *****************')
                print()
                print()
                pygame.quit()
                exit()
    return

def distance_filter(current_length, previous_length):
    # filters max length only to course max length distances
    # current_length is the sensors realtime current reading
    max_course_value = 2000 # current max straight length in mm

    if current_length > max_course_value:
        current_length = previous_length
        return current_length   # updated current length
    else: 
        return()    # return nothing... value ok

    

def write_robot_csv_file():
    # write to: robot_data.csv
    time_stamp = time.time()
    writer.writerow({
        'timestamp': time_stamp,
        'joystick_throttle': throttle,
        'joystick_direction': direction,
        'distance_L': distance_L,
        'distance_C': distance_C,
        'distance_R': distance_R,
    })
    return

def print_distances():
    # Display distances to the terminal
    print()
    print('*************************************************************')
    print(f"Distance to Left sensor: {distance_L:.2f} mm")
    print(f"Distance to Center sensor: {distance_C:.2f} mm")
    print(f"Distance to Right sensor: {distance_R:.2f} mm")
    return

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

# initialize CSV file writing
with open(csv_file_path, mode='w', newline='') as csv_file:
    fieldnames=['timestamp','joystick_throttle', 'joystick_direction', 'distance_L', 'distance_C', 'distance_R']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Main control loop
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            # function: button 4 press aborts program
            emergency_stop()

            # Get joystick axis values
            #throttle = joystick.get_axis(LEFT_JOYSTICK_Y)  # Range: -1 to 1

            # remove auto_throttle and un-comment above throttle 
            # to revert back to manual throttle control

            # auto_throttle provides automatic full-throttle on start up
            throttle = auto_throttle(throttle)
            direction = joystick.get_axis(RIGHT_JOYSTICK_X)  # Range: -1 to 1

            # Dead zone logic ... buffer for initial joystick movement
            # un-comment throttle to go back to manual throttle control
            #if abs(throttle) < DEAD_ZONE: 
                #throttle = 0
            if abs(direction) < DEAD_ZONE:
                direction = 0

            # Compute motor speeds based on joystick input and speed factor
            left_speed = (-throttle - direction) * feel_the_need_for_speed
            right_speed = (-throttle + direction) * feel_the_need_for_speed

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

            # Get distance readings from sensors every 0.25 seconds
            # retrieved via sensor_readings.py script
            if pygame.time.get_ticks() % 250 < 100:  # Every 250 ms
                distances = read_sensor_data()  # read via function in sensor_raedings.py script
                distance_L = distances['distance_L']
                distance_C = distances['distance_C']
                distance_R = distances['distance_R']
                
                # final distance, throttle, direction readings round to 2 decimal places
                distance_L = round(distance_L,2)
                distance_C = round(distance_C,2)
                distance_R = round(distance_R,2)
                throttle = round(throttle,2)
                direction = round(direction,2)

                # function writes robot_data.csv file
                write_robot_csv_file()  
               
            # function displays sensor distance to terminal
            print_distances()   
            
            # Sleep briefly to reduce CPU load
            sleep(0.1)

    # ctrl-c can also be used to exit via interrupt
    except KeyboardInterrupt:   
        pass

    finally:
        # power down the robot program
        motor_left_forward.value = 0
        motor_left_backward.value = 0
        motor_right_forward.value = 0
        motor_right_backward.value = 0
        left_motor_enable.off()
        right_motor_enable.off()
        pygame.quit()
