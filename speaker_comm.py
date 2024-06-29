import os
import pickle

import settings

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

settings = settings.Settings()

if os.path.exists("settings/settings.bin"):
    with open('settings/settings.bin', 'rb') as inp:
        settings = pickle.load(inp)
        print(settings.to_json())


def enable():
    settings.enabled = 1
    print("enable")


def disable():
    settings.enabled = 0
    print("disable")


def set_volume(volume):
    if settings.volume < volume < max_volume:
        for volume_step in range(settings.volume, volume):
            print(f"volume is {real_volume[volume_step]}")
        settings.volume = volume
        write_settings(settings)
    elif settings.volume > volume > min_volume:
        for volume_step in reversed(range(volume, settings.volume)):
            print(f"volume is {real_volume[volume_step]}")
        settings.volume = volume
        write_settings(settings)


def set_input(input):
    print(f"input is {input}")
    settings.input = input
    write_settings(settings)


def set_sw(sw):
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
