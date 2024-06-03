import paramiko
import json
import os

def get_instance_files(instance_name):
    instance_dir = os.path.join('instances', instance_name)
    config_file = os.path.join(instance_dir, 'config.json')
    buttons_file = os.path.join(instance_dir, 'buttons.json')
    ping_file = os.path.join(instance_dir, 'ping_results.json')
    return config_file, buttons_file, ping_file

def load_config(instance_name):
    config_file, _, _ = get_instance_files(instance_name)
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(instance_name, config):
    config_file, _, _ = get_instance_files(instance_name)
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as f:
        json.dump(config, f)

def load_buttons(instance_name):
    _, buttons_file, _ = get_instance_files(instance_name)
    if os.path.exists(buttons_file):
        with open(buttons_file, 'r') as f:
            return json.load(f)
    return []

def save_buttons(instance_name, buttons):
    _, buttons_file, _ = get_instance_files(instance_name)
    os.makedirs(os.path.dirname(buttons_file), exist_ok=True)
    with open(buttons_file, 'w') as f:
        json.dump(buttons, f)

def load_ping_results(instance_name):
    _, _, ping_file = get_instance_files(instance_name)
    if os.path.exists(ping_file):
        with open(ping_file, 'r') as f:
            return json.load(f)
    return []

def save_ping_results(instance_name, ping_results):
    _, _, ping_file = get_instance_files(instance_name)
    os.makedirs(os.path.dirname(ping_file), exist_ok=True)
    with open(ping_file, 'w') as f:
        json.dump(ping_results, f)

def generate_ssh_key():
    ssh_dir = os.path.expanduser('~/.ssh')
    key_path = os.path.join(ssh_dir, 'id_rsa')
    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file(key_path)
    return key

def get_public_key():
    ssh_dir = os.path.expanduser('~/.ssh')
    key_path = os.path.join(ssh_dir, 'id_rsa')
    key = paramiko.RSAKey(filename=key_path)
    return f"{key.get_name()} {key.get_base64()}"

def execute_ssh_command(host, port, username, password, command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port, username, password)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        client.close()
        return output
    except Exception as e:
        return str(e)

def execute_ssh_command_with_key(host, port, username, command):
    try:
        ssh_dir = os.path.expanduser('~/.ssh')
        key_path = os.path.join(ssh_dir, 'id_rsa')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key = paramiko.RSAKey(filename=key_path)
        client.connect(host, port, username, pkey=key)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        client.close()
        return output
    except Exception as e:
        return str(e)
