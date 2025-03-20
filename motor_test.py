##############################################################
#
#   Simple motor test control:
#
#   Motors run forward 3 seconds then backwards 3 seconds
#
##############################################################

from gpiozero import Motor, PWMOutputDevice
from time import sleep

# Define GPIO pins for the left motor
left_motor_forward = 22  # IN1
left_motor_backward = 23  # IN2
left_motor = Motor(forward=left_motor_forward, backward=left_motor_backward)

# Define GPIO pins for the right motor
right_motor_forward = 17  # IN3
right_motor_backward = 18  # IN4
right_motor = Motor(forward=right_motor_forward, backward=right_motor_backward)

# PWMOutpuDevice for motor speeds
left_motor_enable = PWMOutputDevice(25) # ENA connected to gpio 24
right_motor_enable = PWMOutputDevice(24) # ENB connected to gpio 25

try:

    # test Move forward
    print("Moving forward...")
    left_motor_enable.on()  # enable motor A
    left_motor.forward()
    right_motor_enable.on() # enable motor B
    right_motor.forward()
    sleep(3)                # move forward 3 sec

    # test stopping
    print("Stopping.....")
    left_motor.stop()
    right_motor.stop()
    left_motor_enable.off()     # disable motor A
    right_motor_enable.off()    # disable motor B
    sleep(3)

    # test move backward
    print("Moving backward...")
    left_motor_enable.on()  # enable motor A
    left_motor.backward()
    right_motor_enable.on() # enable motor B
    right_motor.backward()
    sleep(3)                # move backward 3 sec

    # Stop the motors
    print("Stopping...")
    left_motor.stop()
    right_motor.stop()
    left_motor_enable.off()     # disable motor A
    right_motor_enable.off()    # disable motor B
  
    sleep(2)

except KeyboardInterrupt:
    # Clean up on exit
    print("....stopped by user........")
finally:
    left_motor.stop()
    right_motor.stop()
    left_motor_enable.off()     # disable motor A
    right_motor_enable.off()    # disable motor B
    print("GPIO release complete...")
