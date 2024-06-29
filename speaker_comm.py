import atexit
import logging
import os
import pickle
import time

import RPi.GPIO as GPIO
import smbus2

import settings

logging.getLogger().setLevel(logging.INFO)

stby = 27
mute = 17
DEVICE_ADDRESS = 68

max_volume = 57
min_volume = 0

max_offset = 10
min_offset = -10

real_volume = [
    63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50,
    49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36,
    35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22,
    21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6
]

sw_positive_offset = [-59, -60, -61, -62, -63, -64]

sw_negative_offset = [-49, -50, -51, -52, -53, -54, -55, -56, -57, -58, -59]

inputs = [
    0b01000100, 0b01000101, 0b01000110
]

settings = settings.Settings()

if os.path.exists("settings.bin"):
    with open('settings.bin', 'rb') as inp:
        settings = pickle.load(inp)

try:
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(stby, GPIO.OUT)
    GPIO.setup(mute, GPIO.OUT)

    GPIO.output(stby, GPIO.LOW)
    GPIO.output(mute, GPIO.LOW)

    bus = smbus2.SMBus(1)
    logging.info("Starting remote amp...")
    GPIO.output(stby, GPIO.HIGH)
    logging.info("Initializing bus...")
    time.sleep(1)

    response = bus.write_quick(DEVICE_ADDRESS)
    if response is not None:
        GPIO.output(mute, GPIO.LOW)
        GPIO.output(stby, GPIO.LOW)
        raise OSError
    else:
        logging.info("Initialization complete")
except OSError:
    logging.error("Speaker initialization failed")
    GPIO.output(mute, GPIO.LOW)
    GPIO.output(stby, GPIO.LOW)
    raise OSError
finally:
    GPIO.output(mute, GPIO.LOW)
    GPIO.output(stby, GPIO.LOW)

if os.path.exists("settings/settings.bin"):
    with open('settings/settings.bin', 'rb') as inp:
        settings = pickle.load(inp)
        print(settings.to_json())


async def enable():
    logging.info("Enabling speakers...")
    GPIO.output(stby, GPIO.HIGH)

    bus = smbus2.SMBus(1)
    logging.info("Starting remote amp...")
    GPIO.output(stby, GPIO.HIGH)
    logging.info("Initializing bus...")
    time.sleep(1)

    bus.write_byte(DEVICE_ADDRESS, 0b10000000)

    bus.write_byte(DEVICE_ADDRESS, 0b10100000)

    bus.write_byte(DEVICE_ADDRESS, 0b01110111)

    bus.write_byte(DEVICE_ADDRESS, 0b01100111)

    bus.write_byte(DEVICE_ADDRESS, 0b11000101)

    bus.write_byte(DEVICE_ADDRESS, 0b11000101)

    bus.write_byte(DEVICE_ADDRESS, 0b11100101)

    bus.write_byte(DEVICE_ADDRESS, 0b01000101)

    bus.write_byte(DEVICE_ADDRESS, 0b01000100)

    bus.write_byte(DEVICE_ADDRESS, 0b00111111)

    bus.write_byte(DEVICE_ADDRESS, 0b10000000)

    GPIO.output(mute, GPIO.HIGH)

    time.sleep(1)

    increase_volume(min_volume, settings.volume)

    set_input(settings.input)

    settings.enabled = 1
    print("enabled")
    return 1


async def disable():
    logging.info("Shutting down remote amp...")
    decrease_volume(settings.volume, min_volume)
    GPIO.output(mute, GPIO.LOW)
    GPIO.output(stby, GPIO.LOW)
    settings.enabled = 0
    print("disable")


def set_volume(volume):
    if settings.volume < volume < max_volume:
        increase_volume(settings.volume, volume)
    elif settings.volume > volume > min_volume:
        decrease_volume(settings.volume, volume)
    settings.volume = volume
    write_settings(settings)


def increase_volume(current_volume, new_volume):
    for volume_step in range(current_volume, new_volume):
        print(f"volume is {real_volume[volume_step]}")
        bus.write_byte(DEVICE_ADDRESS, real_volume[volume_step])


def decrease_volume(current_volume, new_volume):
    for volume_step in reversed(range(new_volume, current_volume)):
        print(f"volume is {real_volume[volume_step]}")
        bus.write_byte(DEVICE_ADDRESS, real_volume[volume_step])


def set_input(input):
    print(f"input is {input}")
    bus.write_byte(DEVICE_ADDRESS, inputs[input])
    settings.input = input
    write_settings(settings)


def set_sw(sw):
    for volume_step in range(settings.sw, sw):
        if sw > 0 and (volume_step % 2) == 0:
            print(f"volume is {sw_positive_offset[volume_step // 2]}")
            settings.volume = sw
            write_settings(settings)
        else:
            for volume_step in reversed(range(sw, settings.sw)):
                print(f"volume is {sw_negative_offset[volume_step]}")
            settings.volume = sw
            write_settings(settings)
            print(f"sw is {sw}")
    settings.sw = sw
    write_settings(settings)


def set_bass(bass):
    print(f"bass is {bass}")
    settings.bass = bass
    write_settings(settings)


def set_treble(treble):
    print(f"treble is {treble}")
    settings.treble = treble
    write_settings(settings)


def set_balance(balance):
    print(f"balance is {balance}")
    settings.balance = balance
    write_settings(settings)


def write_settings(saved_settings):
    with open("settings/settings.bin", 'wb') as outp:
        pickle.dump(saved_settings, outp, pickle.HIGHEST_PROTOCOL)


def get_settings():
    return settings


def exit_handler():
    disable()


atexit.register(exit_handler)
