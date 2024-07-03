import logging
import time

import RPi.GPIO as GPIO
import smbus2

logging.getLogger()

stby_pin = 27
mute_pin = 17
isInit = False

class I2CBus_init:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(stby_pin, GPIO.OUT)
        GPIO.setup(mute_pin, GPIO.OUT)
        GPIO.output(stby_pin, GPIO.LOW)
        GPIO.output(mute_pin, GPIO.LOW)
        logging.info("Enabling speakers...")
        GPIO.output(stby_pin, GPIO.HIGH)
        time.sleep(1)
        self.bus = smbus2.SMBus(1)
        logging.info("Starting remote amp...")
        GPIO.output(stby_pin, GPIO.HIGH)
        logging.info("Initializing bus...")
        time.sleep(1)

        GPIO.output(stby_pin, GPIO.LOW)
        GPIO.output(mute_pin, GPIO.LOW)
        self.isInit = True


    def ifSpeacerInit(self):
        return isInit