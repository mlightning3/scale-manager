#!/usr/bin/env python3

## Scale Manager
#
# Reads from a SparkFun OpenScale board and communicates that back to the Scrybe system
#
#
# Authors: Matt Kohls
# Copyright 2018, University of Michigan

# Imports
import serial
import sys
import getopt
import time
import socket

## Sets Up Scale
#
# @param serialport is a serial object that is connected to the serial port the scale is connected on
# @param hostconnection is a socket that is connected to the Scrybe server
#
# Handles setting the board up after being turned on (taring and calibrating the scale)
# Asks the user for the state of the scale during the process
#
# Steps involved:
# 1. Remove all weight from scale and tare sensor
# 2. Put a known weight on scale and calibrate to that value
def setup_scale(serialport, hostconnection):
    print('Setting up scale...')
    temp = ''
    while temp != 'Readings:\r\n'.encode('latin-1'):
        temp = serialport.readline() # Repeat until we get to the line before readings from sensor
    line = serialport.readline()
    time.sleep(.1)
    serialport.write('x'.encode('latin-1')) # Get into menu to calibrate board
    temp = serialport.read()
    while temp != '>'.encode('latin-1'):
        temp = serialport.readline() # Repeat till we get to prompt
        if temp == ''.encode('latin-1'):
            serialport.write('x'.encode('latin-1'))

    response = ''
    while response != 'yes':
        hostconnection.send('is scale empty'.encode('UTF-8'))
        response = hostconnection.recv(1024)

    #input('Remove all weight from scale. Press enter to continue...')
    serialport.write('1'.encode('latin-1'))
    temp = ' '
    while temp != '>'.encode('latin-1'):
        temp = serialport.readline()  # Repeat till we get to prompt
        if temp == ''.encode('latin-1'):
            serialport.write('x'.encode('latin-1'))
    # TODO: calibrate with known weight knownweight = input('Put known weight on scale. Enter value: ')
    serialport.write('x'.encode('latin-1'))
    line = serialport.readline()

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
    linedata = line.split(','.encode('latin-1'))
    linedata.pop()
    board_time, weight, units, temperature = linedata
    board_time = board_time.decode('utf-8')
    weight = weight.decode('utf-8')
    units = units.decode('utf-8')
    temperature = temperature.decode('utf-8')
    return weight

## Send Data To Scribe
#
# @param hostconnection is a socket that is connected to the Scrybe server
#
# Updates Scribe with the patient's weight
def send_to_scrybe(value, hostconnection):
    print('...sending...')
    hostconnection.send(bytes(value, 'UTF-8'))


## Main
#
# Sets up the program/hardware, and then goes into loop of reading from scale and sending values
def main(argv):
    # Important Variables and their defaults
    ser = None
    host_socket = None
    tty = '/dev/ttyUSB0'
    baud = 9600
    host_ip = '127.0.0.1'
    port = 8089

    # Command Line Parsing
    try:
        opts, args = getopt.getopt(argv, "ht:b:i:p", ["tty=", "baud=", "ip=", "port="])
    except getopt.GetoptError:
        print ('scale.py -i <ip address>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print('Scale Manager')
            print('Sets-up and reads values from scale and sends to the Scrybe system')
            print('\nUseage: scale.py -i <ip address>')
            print('Optional commands:')
            print('-t <tty device> or --tty=<tty device>    : sets the port to listen to the scale on')
            print('-b <baud> or --baud=<baud>               : sets the baud rate to listen to the scale')
            print('-i <ip address> or --ip=<ip address>     : sets the ip address of the Scrybe host')
            print('-p <port number> or --port=<port number> : sets the port number of the Scrybe host')
            sys.exit()
        elif opt in ("-t", "--tty"):
            tty = arg
        elif opt in ("-b", "--baud"):
            baud = arg
        elif opt in ("-i", "--ip"):
            host_ip = arg
        elif opt in ("-p", "--port"):
            port = arg

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

    print('Connecting to Scrybe at', host_ip, 'on port', port, '...')
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_socket.connect((host_ip, port)) # Defaults to localhost at 8089
    # TODO: error handling
    host_socket.send('scale connecting'.encode('UTF-8'))
    msg = host_socket.recv(1024)
    print('Connected to Scrybe')

    setup_scale(ser, host_socket)

    # When Scribe wants a reading
    print('Weight:', read(ser))
    send_to_scrybe(read(ser))

    host_socket.close()
    ser.close()

# Sets up things when run from the commandline
if __name__ == "__main__":
  main(sys.argv[1:])