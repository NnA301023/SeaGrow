import time
import eventlet
from threading import Thread
from flask_socketio import SocketIO
from data_generator import DataGenerator
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request


def create_app():
    """
    Creates and configures the Flask application with SocketIO
    """
    eventlet.monkey_patch()
    app = Flask(__name__, static_folder='src')
    
    socketio = SocketIO(
        app, 
        message_queue='redis://localhost:6379',
        cors_allowed_origins="*"
    )
    
    return app, socketio

app, socketio = create_app()
schedules = []
current_parameters = {}
history_data = {
    'timestamp': [],
    'temperature': [],
    'salinity': [],
    'acidity': []
}

def background_generator():
    """Background task to generate sensor data"""
    global current_parameters
    generator = DataGenerator()
    while True:
        data = generator.generate_data()
        current_parameters = data
        time.sleep(3)

# Start generator thread when app starts
generator_thread = Thread(target=background_generator, daemon=True)
generator_thread.start()


@app.route('/')
@app.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/input_schedule')
def input_schedule():
    return render_template('input_schedule.html')

@app.route('/api/parameters', methods=['GET'])
def get_parameters():
    return jsonify(current_parameters)

@app.route('/api/parameters', methods=['POST'])
def update_parameters():
    data = request.json
    current_parameters.update(data)
    return jsonify({"status": "success", "data": current_parameters})

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    return jsonify(schedules)

@app.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    
    schedule = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'days': []
    }
    
    for day in range(1, 31):
        current_date = start_date + timedelta(days=day-1)
        schedule['days'].append({
            'day': day,
            'date': current_date.strftime('%Y-%m-%d'),
            'status': 'Ongoing' if day < 30 else 'Ready for Harvest'
        })
    
    schedules.append(schedule)
    return jsonify({"status": "success", "data": schedule})

@app.route('/api/schedules', methods=['DELETE'])
def reset_schedules():
    """
    Clears all schedules and returns success status
    """
    schedules.clear()
    return jsonify({"status": "success"})

@app.route('/api/sensor_history', methods=['GET'])
def get_sensor_history():
    """
    Returns historical sensor data for charts with timestamps
    """ 
    global history_data, current_parameters
    print(history_data)
    print(current_parameters)
    history_data['timestamp'].insert(0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    history_data['temperature'].insert(0, current_parameters['temperature'])
    history_data['salinity'].insert(0, current_parameters['salinity'])
    history_data['acidity'].insert(0, current_parameters['acidity'])
    return jsonify(history_data)

@socketio.on('connect')
def handle_connect():
    """
    Handles client connection event and starts sending sensor data
    """
    print('Client connected')

@socketio.on('sensor_data')
def handle_sensor_data(data):
    """
    Receives sensor data and broadcasts it to all connected clients
    """
    print("Received sensor data:", data)
    global current_parameters
    current_parameters = {
        'temperature': data['temperature'],
        'salinity': data['salinity'],
        'acidity': data['acidity']
    }

@socketio.on_error()
def error_handler(e):
    """
    Handles SocketIO errors
    """
    print(f'SocketIO error: {e}')

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handles client disconnection event
    """
    print('Client disconnected')

if __name__ == '__main__':
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Failed to start server: {str(e)}")