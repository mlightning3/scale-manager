#!/usr/bin/env python3

## Scale Manager
#
# Reads from a SparkFun OpenScale board and communicates that back to the Scribe system
#
#
# Authors: Matt Kohls
# Copyright 2018, University of Michigan

# Imports
import serial
import sys, getopt, time

## Sets Up Scale
#
# @param serialport is a serial object that is connected to the serial port the scale is connected on
#
# Handles setting the board up after being turned on (taring and calibrating the scale)
# Asks the user for the state of the scale during the process
#
# Steps involved:
# 1. Remove all weight from scale and tare sensor
# 2. Put a known weight on scale and calibrate to that value
def setup_scale(serialport):
    print('Setting up scale...')
    temp = ''
    while temp != 'Readings:\r\n'.encode('latin-1'):
        temp = serialport.readline() # Repeat until we get to the line before readings from sensor
        #print(temp)
    line = serialport.readline()
    #print(line)
    time.sleep(.1)
    serialport.write('x'.encode('latin-1')) # Get into menu to calibrate board
    temp = serialport.read()
    #print(temp)
    while temp != '>'.encode('latin-1'):
        temp = serialport.readline() # Repeat till we get to prompt
        #print(temp)
        if temp == ''.encode('latin-1'):
            serialport.write('x'.encode('latin-1'))
    input('Remove all weight from scale. Press enter to continue...')
    serialport.write('1'.encode('latin-1'))
    temp = ' '
    while temp != '>'.encode('latin-1'):
        temp = serialport.readline()  # Repeat till we get to prompt
        #print(temp)
        if temp == ''.encode('latin-1'):
            serialport.write('x'.encode('latin-1'))
    # TODO: calibrate with known weight knownweight = input('Put known weight on scale. Enter value: ')
    serialport.write('x'.encode('latin-1'))
    line = serialport.readline()
    #print(line)

## Read Sensor
#
# @param serialport is a serial object that is connected to the serial port the scale is connected on
# @return string of the weight read by the scale
#
# Reads a line from the board, storing the measured weight. The format of the string from the board is:
#       time,weight,units,temperature,
# With the time being in milliseconds since the board powered on, units being either lbs or kg, and temperature in celsius
def read(serialport):
    serialport.write('t'.encode('latin-1'))
    line = serialport.readline()
    while line == ''.encode('latin-1'):
        serialport.write('t'.encode('latin-1'))
        line = serialport.readline()
        #print(line)
    linedata = line.split(','.encode('latin-1'))
    linedata.pop()
    #print(linedata)
    time, weight, units, temperature = linedata
    time = time.decode('utf-8')
    weight = weight.decode('utf-8')
    units = units.decode('utf-8')
    temperature = temperature.decode('utf-8')
    return weight

## Send Data To Scribe
#
# Updates Scribe with the patient's weight
def send_to_scribe():
    print('...sending...')


## Main
#
# Sets up the program/hardware, and then goes into loop of reading from scale and sending values
def main(argv):
    # Global Variables
    ser = 0
    tty = '/dev/ttyUSB0'
    baud = 9600

    # Command Line Parsing
    try:
        opts, args = getopt.getopt(argv, "ht:b", ["tty=", "baud="])
    except getopt.GetoptError:
        print ('scale.py -t <tty device> -b <baud>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print('Scale Manager')
            print('Sets-up and reads values from scale and sends to the Scribe system')
            print ('Useage: scale.py -t <tty device> -b <baud>')
            sys.exit()
        elif opt in ("-t", "--tty"):
            tty = arg
        elif opt in ("-b", "--baud"):
            baud = arg

    print('Opening serial port', tty, 'at', baud, 'baud...')
    try:
        ser = serial.Serial(tty, baud, timeout=1) # This defaults to /dev/ttyUSB0 at 9600 baud if nothing was passed in
    except ValueError as ve: # Some value we passed in was bad
        print(ve)
        exit(2)
    except serial.SerialException as se: # Unable to find tty device
        print(se)
        exit(2)
    else:
        print('Serial port opened')

    # When we get the signal the scale is ready for setup
    setup_scale(ser)

    # When Scribe wants a reading
    print('Weight:', read(ser))
    send_to_scribe()

    ser.close()

# Sets up things when run from the commandline
if __name__ == "__main__":
  main(sys.argv[1:])