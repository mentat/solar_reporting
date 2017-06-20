import os
import sys
import json
import urllib
import urllib2
import datetime

from pymodbus.client.sync import ModbusTcpClient

PV_OUTPUT_KEY = os.getenv("PV_OUTPUT_KEY")
PV_SYSTEM_ID = os.getenv("PV_SYSTEM_ID")

RADIAN_ADDRESS = "192.168.2.42"

MIDNIGHT_ADDRESS = "192.168.2.46"

MIDNIGHT_REGISTERS = {
    "BATT_VOLTS": 4114,
    "PV_VOLTS": 4115,
}

class SolarMonitor(object):

    def read_charger(self):
        client = ModbusTcpClient(MIDNIGHT_ADDRESS)
        base = 4114
        rq = client.read_holding_registers(base,40)
        assert(rq.function_code < 0x80)

        batt_v = rq.registers[4114-base]/10.0
        pv_v = rq.registers[4115-base]/10.0
        in_kwh = rq.registers[4117-base]/10.0
        in_watt = rq.registers[4118-base]
        in_amp_hours = rq.registers[4124-base]/10.0
        inv_system_temp = rq.registers[4131-base]/10.0

        return (batt_v, pv_v, in_kwh, in_watt, in_amp_hours, inv_system_temp)

        #self.upload_status(KWH, WATT, TEMP, BATTV)

    def read_inverter(self):
        # The radian returns JSON, thankfully
        f = urllib2.urlopen('http://%s/Dev_status.cgi?&Port=0' % RADIAN_ADDRESS)

        data = json.loads(f.read())

        assert "devstatus" in data

        port_data_1 = data["devstatus"]["ports"][0]

        l1_volts = port_data_1["VAC_out_L1"]
        l2_volts = port_data_1["VAC_out_L2"]
        l1_amps = port_data_1["Inv_I_L1"]
        l2_amps = port_data_1["Inv_I_L2"]

        out_watts = l1_volts*l1_amps + l2_volts*l2_amps

        port_data_2 = data["devstatus"]["ports"][1]

        out_kwh = port_data_2["Out_kWh_today"]
        out_ah = port_data_2["Out_AH_today"]

        return (out_kwh, out_ah, out_watts)


    def upload_status(self):

        batt_v, pv_v, in_kwh, in_watt, in_amp_hours, inv_system_temp = self.read_charger()
        out_kwh, out_ah, out_watts = self.read_inverter()

        dt = datetime.datetime.utcnow()
        #ts = time.mktime(dt.timetuple())

        params = {
            'd':dt.strftime("%Y%m%d"), # date 20100830
            't':dt.strftime("%H:%M"), # time 14:12
            'v1':in_kwh * 1000, # energy generated (wh)
            'v2':in_watt, # power generated (watts)
            'v3':out_kwh * 1000, # Energy consumption (wh)
            'v4':out_watts, # Power consumption (watts)
            #'v5':temp, # Temperature (outside, ambient?)
            'v6': pv_v, # PV voltage, I think.
        }

        print "Sending: %s" % params
        return

        req = urllib2.Request(
            url='https://pvoutput.org/service/r2/addstatus.jsp',
            data=urllib.urlencode(params))
        req.add_header('X-Pvoutput-Apikey', PV_OUTPUT_KEY)
        req.add_header('X-Pvoutput-SystemId', PV_SYSTEM_ID)

        r = urllib2.urlopen(req)

        if r.getcode() != 200:
            print "Could not post data: %s" % r.read()
            sys.exit(1)

    def upload_daily(self):
        # Maybe not needed since doing status every 15 min
        params = {
            'd':'', # date
            'g':'', # generated
            'pp':'', # peak power
            'c':'', # consumption
        }

        req = urllib2.Request(
            url='https://pvoutput.org/service/r2/addoutput.jsp',
            data=urllib.urlencode(params))
        req.add_header('X-Pvoutput-Apikey', PV_OUTPUT_KEY)
        req.add_header('X-Pvoutput-SystemId', PV_SYSTEM_ID)

        r = urllib2.urlopen(req)

if __name__=="__main__":
    if not PV_OUTPUT_KEY:
        print "Please set the evironmental variables: PV_OUTPUT_KEY and PV_SYSTEM_ID."
        sys.exit(1)

    sm = SolarMonitor()
    sm.upload_status()
