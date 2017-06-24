MATE3 = [
    {'length': 65, 'model': 1, 'name': 'CommonBlock', 'offset': 40069},
    {'length': 420, 'model': 64110, 'name': 'OutbackDeviceIdentifier', 'offset': 40491},
    {'length': 27, 'model': 64120, 'name': 'OutbackSystemControl', 'offset': 40520},
    {'length': 50, 'model': 102, 'name': 'SplitPhaseIntegerInverter', 'offset': 40572},
    {'length': 56, 'model': 64255, 'name': None, 'offset': 40630},
    {'length': 58, 'model': 64115, 'name': 'OutbackSplitPhaseRadianInverter', 'offset': 40690},
    {'length': 88, 'model': 64116, 'name': 'OutbackRadianInverterConfiguration', 'offset': 40780},
    {'length': 76, 'model': 64118, 'name': 'OutbackFLEXNetDCRealTime', 'offset': 40858},
    {'length': 52, 'model': 64119, 'name': 'OutbackFLEXNetDCConfiguration', 'offset': 40912}
]

SCALES = {

    "GS_Split_kWh_SF": {
        "start":43,
        "end":43,
        "size":1,
        "type":"int16",
        "value": None
    },
    "GS_Split_DC_Voltage_SF ": {
        "start":4,
        "end":4,
        "size":1,
        "type":"int16",
        "value": None
    },
    "GS_Split_AC_Current_SF": {
        "start":5,
        "end":5,
        "size":1,
        "type":"int16",
        "value": None
    },
    "GS_Split_AC_Voltage_SF": {
        "start":6,
        "end":6,
        "size":1,
        "type":"int16",
        "value": None
    },
    "GS_Split_AC_Frequency_SF": {
        "start":7,
        "end":7,
        "size":1,
        "type":"int16",
        "value": None
    },
}
LOCATIONS = {
    64115: 40630,
    64118: 40780,
}
DIDS = {
    102: {
        "WH": {
            "start":22,
            "end":23,
            "size":1,
            "rw":"R",
            "type":"acc32",
            "units":"kWh",
            "scale_factor": "FN_kW_SF",
            "description":"AC Energy"
        },

    },
    64118: {
        "FN_Output_kW": {
            "start":25,
            "end":25,
            "size":1,
            "rw":"R",
            "type":"uint16",
            "units":"kW",
            "scale_factor": "FN_kW_SF",
            "description":"Total_output_kWatts"
        },

    },
    64115: {
        # 64115 48 48 1 R GS_Split_L1_Output_kWh uint16 kWh GS_Split_kWh_SF Measured Daily Output L1 kWh
        "GS_Split_L1_Output_kWh": {
            "start":48,
            "end":48,
            "size":1,
            "rw":"R",
            "type":"uint16",
            "units":"kWh",
            "scale_factor": "GS_Split_kWh_SF",
            "description":"Measured Daily Output L1 kWh"
        },
        "GS_Split_L2_Output_kWh": {
            "start":53,
            "end":53,
            "size":1,
            "rw":"R",
            "type":"uint16",
            "units":"kWh",
            "scale_factor": "GS_Split_kWh_SF",
            "description":"Measured Daily Output L2 kWh"
        },
        "GS_Split_Load_kW": {
            "start":59,
            "end":59,
            "size":1,
            "rw":"R",
            "type":"uint16",
            "units":"kW",
            "scale_factor": "GS_Split_kWh_SF",
            "description":"Load kW"
        },
        "GS_Split_Output_kW": {
            "start":55,
            "end":55,
            "size":1,
            "rw":"R",
            "type":"uint16",
            "units":"kW",
            "scale_factor": "GS_Split_kWh_SF",
            "description":"Output kW"
        },
        "GS_Split_Charger_kWh": {
            "start":54,
            "end":54,
            "size":1,
            "rw":"R",
            "type":"uint16",
            "units":"kWh",
            "scale_factor": "GS_Split_kWh_SF",
            "description":"Daily Charger kWh"
        },
        "GS_Split_AC1_L1_Buy_kWh": {
            "start":49,
            "end":49,
            "size":1,
            "rw":"R",
            "type":"uint16",
            "units":"kWh",
            "scale_factor": "GS_Split_kWh_SF",
            "description":"Daily AC1 Buy L2 kWh"
        },
    }
}
#

def read_outback_modbus(client):

    results = {}

    rq = client.read_holding_registers(40520, 50)
    print rq.registers

    for key, value in DIDS[102].iteritems():
        if value["start"] != value["end"]:
            start = rq.registers[value["start"]-1]
            end = rq.registers[value["end"]-1]
            actual_value = (end << 16) + start
        else:
            actual_value = rq.registers[value["start"]-1]/1000.0

        results[key] = actual_value / 1000.0

    rq = client.read_holding_registers(40630, 60)
    print rq.registers

    for key, value in DIDS[64115].iteritems():
        #print SCALES[value["scale_factor"]]["value"]
        print "%s: %s %s (%s)" % (
            value["description"],
            rq.registers[value["start"]-1]/10.0,
            value["units"], key)
        results[key] = rq.registers[value["start"]-1]/10.0

    rq = client.read_holding_registers(40780, 78)
    print rq.registers
    for key, value in DIDS[64118].iteritems():
        #print SCALES[value["scale_factor"]]["value"]
        print "%s: %s %s (%s)" % (
            value["description"],
            rq.registers[value["start"]-1]/10.0,
            value["units"], key)
        results[key] = rq.registers[value["start"]-1]/10.0
    print results
    out_kwh = results["GS_Split_L1_Output_kWh"] + results["GS_Split_L2_Output_kWh"]
    out_ah = 0
    out_watts = results["GS_Split_Load_kW"]

    return out_kwh, out_ah, int(out_watts * 1000)
