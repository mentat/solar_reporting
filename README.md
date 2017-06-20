# Solar Reporting

This code pulls data from an Outback Radian with a Mate3 and a Midnight
Classic 200 charge controller and sends it to PVOutput.org.  It can be
modified easily to send the data anywhere.

Your Mate3 and Classic need to be connected to your local network and
assigned IP addresses for this to work.  Also, make sure you are running
the latest firmware.

## Setup

First edit solar.py and replace your actual IP addresses for the Mate3 and
Classic.

Then make sure you have pymodbus installed:

```
pip install pymodbus
```

## Run

```
export PV_OUTPUT_KEY=<your pvoutput.org api key here>
export PV_SYSTEM_ID=<your pvoutput.org system id here>
python solar.py
```
