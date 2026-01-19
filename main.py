from microdot import Microdot
import _thread
import json
import time
import gc
import machine
import esp32
from serial import get_data

app = Microdot()
json_data = {}
data_lock = _thread.allocate_lock()

# Global watchdog timer
wdt = machine.WDT(timeout=60000) # Timeout after 60 seconds

def create_temperatures(d):
    output = [
        "# TYPE p4_temperatures_celsius gauge",
        "# UNIT p4_temperatures_celsius celsius",
        "# HELP p4_temperatures_celsius collected via RS232 from P4 Pellets"
        ]
    for key in d:
        sensor = json_data[key]['sensor']
        factor = json_data[key]['factor']
        total = json_data[key]['total']
        if key in ['2', '3', '11', '17', '18', '20', '21', '23', '24', '25', '28']:
            if factor == 1:
                metric = 'p4_temperatures_celsius{sensor="%s"} %.1d' % (sensor, total)
            else:
                metric = 'p4_temperatures_celsius{sensor="%s"} %.1f' % (sensor, total)
            output.append(metric)
    esp_temp_celsius = (esp32.raw_temperature() - 32) * 5 / 9
    temp_data = 'p4_temperatures_celsius{sensor="ESP32 temperature"} %.1f' % esp_temp_celsius
    output.append(temp_data)
    return '\n'.join(output)

def create_states(d):
    output = [
        "# TYPE p4_states stateset",
        "# HELP p4_states collected via RS232 from P4 Pellets"
        ]
    for key in d:
        sensor = json_data[key]['sensor']
        value = json_data[key]['value']
        if key in ['26', '27']:
            metric = 'p4_states{sensor="%s"} %.1d' % (sensor, value)
            output.append(metric)
    return '\n'.join(output)

def create_values(d):
    output = [
        "# TYPE p4_values gauge",
        "# HELP p4_values collected via RS232 from P4 Pellets"
        ]
    for key in d:
        sensor = json_data[key]['sensor']
        factor = json_data[key]['factor']
        total = json_data[key]['total']
        if key in ['4', '5', '6', '7', '8', '9', '12', '13', '14', '22', '30']:
            if factor == 1:
                metric = 'p4_values{sensor="%s"} %.1d' % (sensor, total)
            else:
                metric = 'p4_values{sensor="%s"} %.1f' % (sensor, total)
            output.append(metric)
    memory_data = 'p4_values{sensor="ESP32 free memory"} %.1d' % gc.mem_free()
    output.append(memory_data)
    return '\n'.join(output)

def create_info(d):
    status = ""
    fehler = ""
    output = [
        "# TYPE p4_info info"
        ]
    for key in d:
        sensor = json_data[key]['sensor']
        total = json_data[key]['total']
        if key == '1':
            status = sensor
        if key == '99':
            fehler = total
    metric = 'p4_info{status="%s",fehler="%s"} 1' % (status, fehler)
    output.append(metric)
    return '\n'.join(output)

def create_metrics():
    output = []
    with data_lock:
        output.append(create_temperatures(json_data))
        output.append(create_states(json_data))
        output.append(create_values(json_data))
        output.append(create_info(json_data))
        output.append("# EOF")
    wdt.feed()
    return '\n'.join(output)

def data_thread():
    global json_data
    while True:
        with data_lock:
            json_data = get_data()
        gc.collect()
        # print("Sensor daten aktualisiert:", json.dumps(json_data, separators=None))
        print("Sensor daten aktualisiert...")
        time.sleep(30)  # Messintervall (Sekunden)
        wdt.feed()

@app.route('/metrics')
async def metrics(request):
    return create_metrics(), 200, {'Content-Type': 'application/openmetrics-text'}


@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

# Threads starten
_thread.start_new_thread(data_thread, ())
app.run(debug=True, port=9100)
