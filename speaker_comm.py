import logging
import os
import pickle
import time

from gpiozero import DigitalOutputDevice
from smbus2 import smbus2

import settings

logging.getLogger().setLevel(logging.INFO)

DEVICE_ADDRESS = 68
max_volume = 57
min_volume = 0

stby_pin = 27
mute_pin = 17

max_sw = 16
default_sw = 10
min_sw = 0

rear_right_channel_sw_addr = 0b11000000
rear_left_channel_sw_addr = 0b11100000

real_volume = [
    63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50,
    49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39, 38, 37, 36,
    35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22,
    21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6
]

sw_values = [0b00001111, 0b00001110, 0b00001101, 0b00001100, 0b00001011, 0b00001010, 0b00001001, 0b00001000, 0b00000111,
             0b00000110, 0b00000101, 0b00000100, 0b00000011, 0b00000010, 0b00000001, 0b00000000]

inputs = [
    0b01000100, 0b01000101, 0b01000110
]

settings = settings.Settings()

if os.path.exists("settings/settings.bin"):
    try:
        with open('settings/settings.bin', 'rb') as inp:
            settings = pickle.load(inp)
            print(settings.to_json())
    except EOFError:
        os.remove("settings/settings.bin")

logging.info("Starting remote amp...")
stby = DigitalOutputDevice(stby_pin)
mute = DigitalOutputDevice(mute_pin)
stby.off()
mute.off()
logging.info("Initializing bus...")
bus = smbus2.SMBus(1)
logging.info("Initialization complete")


def start_bus(retry_counter):
    logging.info("Enabling speakers...")
    stby.on()
    retry_counter += 1
    try:
        time.sleep(0.5)
        bus.write_quick(DEVICE_ADDRESS)
    except IOError:
        logging.error(f"Failed to speakers. Retry count is: {retry_counter}")
        if retry_counter < 10:
            logging.info("Retry in 1 seconds...")
            time.sleep(1)
            start_bus(retry_counter)
        else:
            raise IOError


def enable():
    try:
        start_bus(0)
    except IOError:
        return 0

    # front attenuation set to 0
    bus.write_byte(DEVICE_ADDRESS, 0b10000000)
    bus.write_byte(DEVICE_ADDRESS, 0b10100000)

    # sw attenuation set to -6.25dB
    bus.write_byte(DEVICE_ADDRESS, 0b11000101)
    bus.write_byte(DEVICE_ADDRESS, 0b11100101)

    # bass and treble set to 0
    bus.write_byte(DEVICE_ADDRESS, 0b01110111)
    bus.write_byte(DEVICE_ADDRESS, 0b01100111)

    # set input to 0
    bus.write_byte(DEVICE_ADDRESS, 0b01000100)

    # set volume to -80dB
    bus.write_byte(DEVICE_ADDRESS, 0b00111111)

    mute.on()

    time.sleep(1)

    increase_volume(min_volume, settings.volume, real_volume)

    set_sw(default_sw)

    set_input(settings.input)

    settings.enabled = 1
    print("enabled")
    return 1


def disable():
    logging.info("Shutting down remote amp...")
    decrease_volume(settings.volume, min_volume, real_volume)
    mute.off()
    stby.off()
    settings.enabled = 0
    print("disable")
    return 1


def set_volume(volume):
    logging.info(f"Changing volume to {volume}")
    if settings.volume < volume < max_volume:
        increase_volume(settings.volume, volume, real_volume)
    elif settings.volume > volume >= min_volume:
        decrease_volume(settings.volume, volume, real_volume)
    settings.volume = volume
    write_settings(settings)
    logging.info(f"Volume has been changed to {volume}")


def increase_volume(current_volume, new_volume, values_list):
    logging.info(f"Increasing volume from {current_volume} to {new_volume}")
    for volume_step in range(current_volume, new_volume):
        logging.debug(f"value is {values_list[volume_step]}")
        bus.write_byte(DEVICE_ADDRESS, values_list[volume_step])
    logging.info(f"Volume has been increased from {current_volume} to {new_volume}")


def decrease_volume(current_volume, new_volume, values_list):
    logging.info(f"Decreasing volume from {current_volume} to {new_volume}")
    for volume_step in reversed(range(new_volume, current_volume)):
        logging.debug(f"value is {values_list[volume_step]}")
        bus.write_byte(DEVICE_ADDRESS, values_list[volume_step])
    logging.info(f"Volume has been decreased from {current_volume} to {new_volume}")


def increase_sw_volume(current_volume, new_volume, values_list):
    logging.info(f"Increasing sw from {current_volume} to {new_volume}")
    for volume_step in range(current_volume, new_volume):
        logging.debug(f"value is {values_list[volume_step]}")
        bus.write_byte(DEVICE_ADDRESS, rear_right_channel_sw_addr | values_list[volume_step])
        bus.write_byte(DEVICE_ADDRESS, rear_left_channel_sw_addr | values_list[volume_step])
    logging.info(f"SW has been increased from {current_volume} to {new_volume}")


def decrease_sw_volume(current_volume, new_volume, values_list):
    logging.info(f"Decreasing sw from {current_volume} to {new_volume}")
    for volume_step in reversed(range(new_volume, current_volume)):
        logging.debug(f"value is {values_list[volume_step]}")
        bus.write_byte(DEVICE_ADDRESS, rear_right_channel_sw_addr | values_list[volume_step])
        bus.write_byte(DEVICE_ADDRESS, rear_left_channel_sw_addr | values_list[volume_step])
    logging.info(f"SW has been decreased from {current_volume} to {new_volume}")


def set_input(input):
    logging.info(f"Setting input is {input}")
    bus.write_byte(DEVICE_ADDRESS, inputs[input])
    settings.input = input
    write_settings(settings)
    logging.info(f"Input has been set to {input}")


def set_sw(sw):
    logging.info(f"Changing SW to {sw}")
    if settings.sw < sw < max_sw:
        logging.debug("Increasing sw volume")
        increase_sw_volume(settings.sw, sw, sw_values)
    elif settings.sw > sw >= min_sw:
        logging.debug("Decreasing sw volume")
        decrease_sw_volume(settings.sw, sw, sw_values)
    settings.sw = sw
    write_settings(settings)
    logging.info(f"SW has been changed to {sw}")


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
