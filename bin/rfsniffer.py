#!/usr/bin/env python

import sys
import os

p = os.path.dirname(os.path.abspath(__file__))
sys.path.append(p.replace('bin', 'lib'))

import rf_utils
import pickle
import argparse
from datetime import datetime

ON_PI = True

try:
    import RPi.GPIO as gpio
except ImportError as error:
    print('Running not on a pi?: ', error)
    ON_PI = False

RECEIVED_SIGNAL = [[], []]  #[[time of reading], [signal reading]]
MAX_DURATION = 5


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        dest='receive_pin',
        default=20,
        type=int,
        help='Gpio pin to recieve data from'
    )
    parser.add_argument(
        '--dump',
        dest='dump',
        type=str,
        default=None,
        help='Dump data to file using Pickle'
    )
    return parser.parse_args()


def main():
    p_args = args()
    revceive_pin = p_args.receive_pin
    gpio.setmode(gpio.BCM)
    gpio.setup(revceive_pin, gpio.IN)
    cumulative_time = 0
    beginning_time = datetime.now()
    print('**Started recording**')
    while cumulative_time < MAX_DURATION:
        time_delta = datetime.now() - beginning_time
        RECEIVED_SIGNAL[0].append(time_delta)
        RECEIVED_SIGNAL[1].append(gpio.input(revceive_pin))
        cumulative_time = time_delta.seconds
    print('**Ended recording**')
    print(len(RECEIVED_SIGNAL[0]), 'samples recorded')
    gpio.cleanup()

    print('**Processing results**')
    for i in range(len(RECEIVED_SIGNAL[0])):
        RECEIVED_SIGNAL[0][i] = \
            RECEIVED_SIGNAL[0][i].seconds + \
            RECEIVED_SIGNAL[0][i].microseconds/1000000.0

    times, values = RECEIVED_SIGNAL
    code = rf_utils.get_code(times, values)
    print('Code found: ', code)

    # dumping file
    if p_args.dump:
        with open(p_args.dump, 'w') as f:
            pickle.dump(RECEIVED_SIGNAL, f)


if __name__ == '__main__':
    if not ON_PI:
        print('Following args where parsed')
        print(args())
    else:
        main()
