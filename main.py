from microdot import Microdot
import _thread
from serial import get_json

app = Microdot()

html = '''<!DOCTYPE html>
<html>
    <head>
        <title>Microdot Example Page</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <div>
            <h1>Microdot Example Page</h1>
            <p>Hello from Microdot!</p>
            <p><a href="/shutdown">Click to shutdown the server</a></p>
        </div>
    </body>
</html>
'''

def create_temperatures():
    json_data = get_json()
    output = [
        "# TYPE p4_temperatures_celsius gauge",
        "# UNIT p4_temperatures_celsius celsius",
        "# HELP p4_temperatures_celsius collected via RS232 from P4 Pellets"
        ]
    for key in json_data:
        sensor = json_data[key]['sensor']
        total = json_data[key]['total']
        factor = float(json_data[key]['factor'])
        if key in ['2', '3', '11', '17', '18', '20', '21', '23', '24', '25', '28']:
            metric = "p4_temperatures_celsius{sensor='%s'} %.2f" % (sensor, total)
            output.append(metric)
        #output.append(key)
    return '\n'.join(output)

def create_metrics():
    output = []
    output.append(create_temperatures())
    return '\n'.join(output)

@app.route('/metrics')
async def metrics(request):
    return create_metrics(), 200, {'Content-Type': 'application/openmetrics-text'}


@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'


app.run(debug=True, port=9100)
