# PingPlot Version 1.1.0
#### Author: Christopher Campo
#### Email:	ccampo.progs@gmail.com

## Overview
PingPlot is a Python script which pings a given host and records the latency of each ping as a function of time. When 
you choose to stop, a plot is generated showing your latency to the host as a function of time since the startup of the 
program. It utilizes numerous Python libraries and especially takes advantage of Matplotlib and NumPy.

If you experience a timeout (100% packet loss) for a certain amount of time, the plot shows a red-shaded area across the
times your connection to the host was down. This may be useful in diagnosing network connection issues, both client and
server side.

PingPlot is meant to be run as a command line program. The run arguments/options are listed below. If you wish to run 
this program from Windows, create a shortcut, right click on it, scroll down to properties, and then append any of the 
options/arguments below to the target field. To run the program with these arguments, just run the shortcut.

If you have any questions/comments, please feel free to email me at 
[ccampo.progs@gmail.com](mailto@ccampo.progs@gmail.com) or through my github page, github.com/ccampo133. Also feel free
to create issues in this repo's issue tracker.

This application was inspired by [PingPlotter](http://www.pingplotter.com/), which is basically a more robust version 
of this software.

### Example plot (the red bars indicate timeouts):
![](example/example_plot.png)

## Usage

This assumes you have Python (3+) installed on your system.

I recommend using a [virtualenv](https://docs.python.org/3/library/venv.html):
                    
    $ python -m venv venv  

Then activate it:

    $ source venv/bin/activate

Next, install the requirements:

    $ pip install -r requirements.txt

Then run via the command line:

```
Usage: python pingplot.py [options]

Options:
-h, --help      show this help message and exit
-p, --plot      generates plot after data collection is finished
-f, --file      save plot to file in the current directory
-H HOST, --host=HOST the url or ip address to ping [default: google.com]
-n N, --num=N     the number of packets to send on each ping iteration
          [default: 1]
-t DT, --dt=DT    the time interval (seconds) in which successive pings
          are sent [default: 0.5 s]
-l, --log       save a logfile of the event in the current directory
-s SIZE, --size=SIZE If plotting/saving a plot, this is the plot's
          dimensionsin pixels (at 80 DPI) in the format XxY
          [default: 1280x640]
```

Example:

    $ python pingplot.py -H example.com
