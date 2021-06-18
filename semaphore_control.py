#!/usr/bin/python
import RPi.GPIO as GPIO
from time import sleep

from Custom_Class import RepeatedTimer

RED, YELLOW, GREEN = 0, 1, 2

GPIO.cleanup()
sem1 = [15, 13, 11]
sem2 = [23, 21, 19]
sem3 = [33, 31, 29]
sem4 = [40, 38, 36]

pin_list = [15, 13, 11, 23, 21, 19, 33, 31, 29, 40, 38, 36]

GPIO.setmode(GPIO.BOARD)
for PIN in pin_list:
    GPIO.setup(PIN, GPIO.OUT)


# 2 e 4 RED
def red_state():
    GPIO.output(sem2[GREEN], GPIO.LOW)
    GPIO.output(sem4[GREEN], GPIO.LOW)

    GPIO.output(sem2[YELLOW], GPIO.HIGH)
    GPIO.output(sem4[YELLOW], GPIO.HIGH)
    sleep(1)
    GPIO.output(sem2[YELLOW], GPIO.LOW)
    GPIO.output(sem4[YELLOW], GPIO.LOW)
    GPIO.output(sem2[RED], GPIO.HIGH)
    GPIO.output(sem4[RED], GPIO.HIGH)

    sleep(0.7)
    GPIO.output(sem1[GREEN], GPIO.HIGH)
    GPIO.output(sem3[GREEN], GPIO.HIGH)

    GPIO.output(sem1[RED], GPIO.LOW)
    GPIO.output(sem3[RED], GPIO.LOW)




def green_state():
    GPIO.output(sem1[GREEN], GPIO.LOW)
    GPIO.output(sem3[GREEN], GPIO.LOW)

    GPIO.output(sem1[YELLOW], GPIO.HIGH)
    GPIO.output(sem3[YELLOW], GPIO.HIGH)
    sleep(1)
    GPIO.output(sem1[YELLOW], GPIO.LOW)
    GPIO.output(sem3[YELLOW], GPIO.LOW)
    GPIO.output(sem1[RED], GPIO.HIGH)
    GPIO.output(sem3[RED], GPIO.HIGH)

    sleep(0.7)
    GPIO.output(sem2[GREEN], GPIO.HIGH)
    GPIO.output(sem4[GREEN], GPIO.HIGH)

    GPIO.output(sem2[RED], GPIO.LOW)
    GPIO.output(sem4[RED], GPIO.LOW)


def setup_emergency_state():
    print("FORA DO FOR")
    for PIN1 in pin_list:
        GPIO.output(PIN1, GPIO.LOW)
        print(str(PIN1) + " OFF ")
    GPIO.output(sem1[RED], GPIO.HIGH)
    GPIO.output(sem2[RED], GPIO.HIGH)
    GPIO.output(sem3[RED], GPIO.HIGH)
    GPIO.output(sem4[RED], GPIO.HIGH)


def normal_loop(sem_event):
    sem_event.clear()
    red_state()
    sleep(5)
    sem_event.set()
    green_state()


def EMS_sem(sem_911):
    GPIO.output(sem_911[RED], GPIO.HIGH)
    GPIO.output(sem_911[GREEN], GPIO.HIGH)
    GPIO.output(sem_911[YELLOW], GPIO.LOW)
    sleep(0.2)
    GPIO.output(sem_911[RED], GPIO.LOW)
    GPIO.output(sem_911[GREEN], GPIO.LOW)
    GPIO.output(sem_911[YELLOW], GPIO.HIGH)


def sem_loop(sem_event):
    for PIN1 in pin_list:
        GPIO.output(PIN1, GPIO.LOW)
    normal_loop(sem_event)
    rt = RepeatedTimer(12, normal_loop, sem_event)
    return rt


def EMS_loop(sem_911):
    EMS_sem(sem_911)
    rt = RepeatedTimer(0.4, EMS_sem, sem_911)
    rt.stop()
    return rt


def master(EMS_event1, EMS_event2, EMS_event3, EMS_event4, sem_event, emsH_event, emsV_event, ems_event):
    state = False
    ems_timer1 = EMS_loop(sem1)
    ems_timer2 = EMS_loop(sem2)
    ems_timer3 = EMS_loop(sem3)
    ems_timer4 = EMS_loop(sem4)
    sem_timer = sem_loop(sem_event)

    while True:
        while EMS_event1.is_set():
            if not state:
                sem_timer.stop()
                while sem_timer.is_running:
                    l = 0
                setup_emergency_state()
                emsH_event.clear()
                emsV_event.clear()
                ems_event.set()
                ems_timer1.start()
                state = True
        while EMS_event2.is_set():
            if not state:
                sem_timer.stop()
                while sem_timer.is_running:
                    l = 0
                setup_emergency_state()
                emsH_event.clear()
                emsV_event.set()
                ems_event.set()
                ems_timer2.start()
                state = True
        while EMS_event3.is_set():
            if not state:
                sem_timer.stop()
                while sem_timer.is_running:
                    l = 0
                setup_emergency_state()
                emsH_event.set()
                emsV_event.clear()
                ems_event.set()
                ems_timer3.start()
                state = True
        while EMS_event4.is_set():
            if not state:
                sem_timer.stop()
                while sem_timer.is_running:
                    l = 0
                setup_emergency_state()
                emsH_event.set()
                emsV_event.set()
                ems_event.set()
                ems_timer4.start()
                state = True
        if state:
            ems_timer1.stop()
            ems_timer2.stop()
            ems_timer3.stop()
            ems_timer4.stop()
            while ems_timer1.is_running or ems_timer2.is_running or ems_timer3.is_running or ems_timer4.is_running:
                print("!!!!!!!!!!!!!!!!!!!No while!!!!!!!!!!!!!!")
            ems_event.clear()
            setup_emergency_state()
            sem_timer = sem_loop(sem_event)
            state = False
    GPIO.cleanup()
