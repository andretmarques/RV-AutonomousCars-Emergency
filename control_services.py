#!/usr/bin/python
import sys, json
RASPBERRY = True
if RASPBERRY == True:
    import RPi.GPIO as GPIO

FREQUENCY = 100
MIN_SPEED = 100


#read pinout configuration information
def read_gpio_conf(field):
    with open('gpio_pins.txt') as json_data:
        data = json.load(json_data)
        json_data.close()
    return data[field]

#init gpio
def gpio_init(gpio_data, pwm_motor):
    gpio_data = read_gpio_conf("gpio_pins")
    if RASPBERRY == True:
       GPIO.setmode(GPIO.BOARD)
    print('GPIO.setmode(GPIO.BOARD)')
    reset_gpio(gpio_data)
    reset_pwm_motor(gpio_data, pwm_motor)
    return (gpio_data, pwm_motor)

#program pin as output and start at LOW
def reset_gpio(gpio_data):
    for key, val in list(gpio_data.items()):
        if val != 0:
            if RASPBERRY == True:
                GPIO.setup(val,GPIO.OUT)
                GPIO.output(val,GPIO.LOW)
            print ('GPIO.setup(',val,',GPIO.OUT)')
            print ('GPIO.output(',val,',GPIO.LOW)')

#program pwm motor frequency and speed
def reset_pwm_motor(gpio_data, pwm_motor):
    for key, val in list(gpio_data.items()):
        if key in ('enable_dir'):
            if RASPBERRY == True:
                pwm_motor[key] = GPIO.PWM(val, FREQUENCY)
                pwm_motor[key].start(MIN_SPEED)
            print ('pwm_motor[',key,'] = GPIO.PWM(',val,',',FREQUENCY,')')
            print ('pwm_motor[',key,'].start(',MIN_SPEED,')')
    return pwm_motor


def control_engines(gpio_data, direction, pwm_motor):
    drive_on = True;
    if direction == 'forward_dir':
        print ('move foward: set set_motion_engine')
        set_motion_engine(gpio_data['forward_dir'], gpio_data['backward_dir'], gpio_data['enable_dir'], gpio_data['enable_turn'])
    elif direction == 'backward_dir':
        print ('move backward: set_motion_engine')
        set_motion_engine(gpio_data['backward_dir'], gpio_data['forward_dir'], gpio_data['enable_dir'], gpio_data['enable_turn'])
    elif direction == 'turn_right':
        print ('turn_right: set_steering_wheel')
        set_steering_wheel(gpio_data['turn_right'], gpio_data['turn_left'], gpio_data['enable_turn'])
    elif direction == 'turn_left':
        print ('turn_left: set_steering_wheel')
        set_steering_wheel(gpio_data['turn_left'], gpio_data['turn_right'], gpio_data['enable_turn'])
    elif direction == 'stop':
        stop_control(gpio_data, pwm_motor)
    elif direction == 'exit':
        drive_on = False
    return drive_on

def set_motion_engine(on_pin, off_pin, enable_pin, disable_pin):
    if RASPBERRY == True:
        GPIO.output(on_pin, GPIO.HIGH)
        GPIO.output(off_pin, GPIO.LOW)
        GPIO.output(enable_pin, GPIO.HIGH)
        GPIO.output(disable_pin, GPIO.LOW)
    print('GPIO.output(',on_pin, ', GPIO.HIGH)')
    print('GPIO.output(',off_pin, ', GPIO.LOW')
    print('GPIO.output(',enable_pin, ', GPIO.HIGH')
    print('GPIO.output(',disable_pin, ', GPIO.LOW')

def set_steering_wheel(on_pin, off_pin, enable_pin):
    if RASPBERRY == True:
        print ('RASPBERRY GPIO:''on', on_pin, 'off', off_pin, 'enable', enable_pin)
        GPIO.output(on_pin, GPIO.HIGH)
        GPIO.output(off_pin, GPIO.LOW)
        GPIO.output(enable_pin, GPIO.HIGH)
    print('GPIO.output(',on_pin, ', GPIO.HIGH)')
    print('GPIO.output(',off_pin, ', GPIO.LOW')
    print('GPIO.output(',enable_pin, ', GPIO.HIGH')

def stop_control(gpio_data, pwm_motor):
    for key, val in list(gpio_data.items()):
        if key in ('forward_dir', 'backward_dir', 'enable_dir', 'turn_left', 'turn_right', 'enable_turn'):
            if RASPBERRY == True:
                GPIO.output(val, GPIO.LOW)
            print('GPIO.output(',val, ', GPIO.LOW)')

def stop_gpio():
    if RASPBERRY == True:
        GPIO.cleanup()
    print('GPIO.cleanup')
