
from flask import Flask, jsonify, request
import random

app = Flask(__name__)

MOCK_SYSTEM_INFO = {
    "@odata.type": "#ComputerSystem.v1_16_0.ComputerSystem",
    "Id": "system",
    "Name": "Computer System",
    "PowerState": "On",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    }
}

MOCK_THERMAL_DATA = {
    "Temperatures": [
        {
            "Name": "CPU1 Temp",
            "ReadingCelsius": 45,
            "Status": {"State": "Enabled", "Health": "OK"}
        },
        {
            "Name": "CPU2 Temp", 
            "ReadingCelsius": 42,
            "Status": {"State": "Enabled", "Health": "OK"}
        },
        {
            "Name": "System Temp",
            "ReadingCelsius": 35,
            "Status": {"State": "Enabled", "Health": "OK"}
        }
    ]
}

@app.route('/redfish/v1/SessionService/Sessions', methods=['POST'])
def create_session():
    """Mock аутентификации"""
    auth_data = request.get_json()
    if auth_data.get('UserName') == 'root' and auth_data.get('Password') == '0penBmc':
        return jsonify({
            "Id": "mock-session-123",
            "UserName": "root"
        }), 201
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/redfish/v1/Systems/system', methods=['GET'])
def get_system():
    """Mock информации о системе"""
    return jsonify(MOCK_SYSTEM_INFO)

@app.route('/redfish/v1/Systems/system/Actions/ComputerSystem.Reset', methods=['POST'])
def reset_system():
    """Mock управления питанием"""
    reset_data = request.get_json()
    reset_type = reset_data.get('ResetType')
    
    if reset_type in ['On', 'ForceOff', 'GracefulShutdown']:
        MOCK_SYSTEM_INFO['PowerState'] = 'On' if reset_type == 'On' else 'Off'
        return jsonify({"message": "Reset action completed"}), 202
    else:
        return jsonify({"error": "Invalid ResetType"}), 400

@app.route('/redfish/v1/Chassis/chassis/Thermal', methods=['GET'])
def get_thermal():
    """Mock данных о температуре"""
    for sensor in MOCK_THERMAL_DATA['Temperatures']:
        if random.random() > 0.7:  
            sensor['ReadingCelsius'] += random.randint(-2, 2)
            sensor['ReadingCelsius'] = max(20, min(80, sensor['ReadingCelsius']))
    
    return jsonify(MOCK_THERMAL_DATA)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
