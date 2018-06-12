# Scale Manager

Scale monitoring and reporting software for the Scrybe system. A project for
the University of Michigan.

### Hardware Requirements

* Computer with network access and serial connection
* Sparkfun OpenScale board connected over serial

# Installing and Setup

Using pip, we can install PySerial like so:

```
$ pip install pyserial
```

Download or clone the repositry to any location of your choosing. The program
can then be run like so:

```
$ python scale.py
```

This defaults to talking to the Sparkfun board at '/dev/ttyUSB0',
and looks for the Scrybe server on 127.0.0.1 which may not be correct. To
change where the program looks for these things with various command line
switches. For example, if you were running this on Windows you might use:

```
$ python scale.py -t COM1 -i 192.168.1.1
```

Which will have the program look for the Sparkfun board on COM1 and connect to
the Scrybe server on 192.168.1.1 . To get a full listing of the available
arguments that can be passed to the program, type:

```
$ python scale.py -h
```

# Copyright

University of Michigan, 2018

All rights reserved