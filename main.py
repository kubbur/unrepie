from flask import Flask, render_template, request, redirect, url_for, jsonify
from app.backend import (
    execute_ssh_command_with_key, load_config, save_config, 
    load_buttons, save_buttons, load_ping_results, save_ping_results,
    generate_ssh_key, get_public_key, execute_ssh_command
)
import json
import os
import time
from ping3 import ping

app = Flask(__name__, template_folder='app/templates')
instances_file = 'instances.json'

def load_instances():
    if os.path.exists(instances_file):
        with open(instances_file, 'r') as f:
            return json.load(f)
    return []

def save_instances(instances):
    with open(instances_file, 'w') as f:
        json.dump(instances, f)

def check_instance_online(host):
    try:
        response_time = ping(host, timeout=2)
        return response_time is not None
    except Exception:
        return False

@app.route('/')
def index():
    instances = load_instances()
    for instance in instances:
        config = load_config(instance['name'])
        instance['online'] = check_instance_online(config.get('host')) if config else False
    return render_template('index.html', instances=instances)

@app.route('/add_instance', methods=['POST'])
def add_instance():
    instances = load_instances()
    name = request.form['name']
    instances.append({'name': name})
    save_instances(instances)
    return redirect(url_for('index'))

@app.route('/delete_instance/<int:index>', methods=['POST'])
def delete_instance(index):
    instances = load_instances()
    if 0 <= index < len(instances):
        del instances[index]
    save_instances(instances)
    return redirect(url_for('index'))

@app.route('/edit_instance/<int:index>', methods=['POST'])
def edit_instance(index):
    instances = load_instances()
    if 0 <= index < len(instances):
        instances[index]['name'] = request.form['name']
    save_instances(instances)
    return redirect(url_for('index'))

@app.route('/instance/<name>')
def instance(name):
    config = load_config(name)
    buttons = load_buttons(name)
    ping_results = load_ping_results(name)
    return render_template('instance.html', instance_name=name, config=config, buttons=buttons, ping_results=ping_results)

@app.route('/instance/<name>/setup', methods=['POST'])
def setup(name):
    host = request.form['host']
    port = int(request.form['port'])
    username = request.form['username']
    password = request.form['password']
    
    # Generate SSH key pair
    key = generate_ssh_key()
    public_key = get_public_key()

    # Save config without password
    config = {
        'host': host,
        'port': port,
        'username': username
    }
    save_config(name, config)

    # Add public key to server's authorized_keys
    command = f'echo "{public_key}" >> ~/.ssh/authorized_keys'
    output = execute_ssh_command(host, port, username, password, command)
    
    return redirect(url_for('instance', name=name))

@app.route('/instance/<name>/execute', methods=['POST'])
def execute(name):
    config = load_config(name)
    if not config:
        return redirect(url_for('instance', name=name))

    host = config.get('host')
    port = config.get('port')
    username = config.get('username')
    command = request.form['command']
    
    output = execute_ssh_command_with_key(host, port, username, command)
    ping_results = load_ping_results(name)
    return render_template('instance.html', instance_name=name, output=output, config=config, buttons=load_buttons(name), ping_results=ping_results)

@app.route('/instance/<name>/add_button', methods=['POST'])
def add_button(name):
    buttons = load_buttons(name)
    button = {
        'name': request.form['name'],
        'command': request.form['command'],
        'confirm': 'confirm' in request.form
    }
    buttons.append(button)
    save_buttons(name, buttons)
    return redirect(url_for('instance', name=name))

@app.route('/instance/<name>/delete_button/<int:index>', methods=['POST'])
def delete_button(name, index):
    buttons = load_buttons(name)
    if 0 <= index < len(buttons):
        del buttons[index]
    save_buttons(name, buttons)
    return redirect(url_for('instance', name=name))

@app.route('/instance/<name>/edit_button/<int:index>', methods=['POST'])
def edit_button(name, index):
    buttons = load_buttons(name)
    if 0 <= index < len(buttons):
        buttons[index]['name'] = request.form['name']
        buttons[index]['command'] = request.form['command']
        buttons[index]['confirm'] = 'confirm' in request.form
    save_buttons(name, buttons)
    return redirect(url_for('instance', name=name))

@app.route('/instance/<name>/ping', methods=['GET'])
def ping_instance(name):
    config = load_config(name)
    host = config.get('host')
    try:
        response_time = ping(host, timeout=2)
        success = response_time is not None
        ping_results = load_ping_results(name)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        ping_results.append({'timestamp': timestamp, 'success': success})
        if len(ping_results) > 5:
            ping_results.pop(0)
        save_ping_results(name, ping_results)
        return jsonify(success=success, timestamp=timestamp)
    except Exception as e:
        return jsonify(success=False, error=str(e))

def run():
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    run()
