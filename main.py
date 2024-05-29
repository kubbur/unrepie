#!/usr/bin/env python3

import curses
import os
import paramiko
import pexpect
import wiringpi as wp
import time
import datetime
import subprocess
import json

config_file = "config.json"

config = {
    "alias": "",
    "username": "",
    "ip_address": ""
}

def load_config():
    global config
    if os.path.exists(config_file):
        with open(config_file, 'r') as file:
            config = json.load(file)
    else:
        configure_server_init()

def save_config():
    global config
    with open(config_file, 'w') as file:
        json.dump(config, file)

def configure_server_init():
    curses.wrapper(configure_server)

def show_warning(stdscr):
    curses.curs_set(1)
    height, width = stdscr.getmaxyx()
    buttons = ["Quit", "Agree", "Configure"]
    current_button = 0

    def draw_screen():
        stdscr.clear()
        warning_text = "WARNING: Please confirm to proceed"
        stdscr.addstr(height // 2 - 2, width // 2 - len(warning_text) // 2, warning_text)

        for idx, button in enumerate(buttons):
            if idx == current_button:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(height // 2 + idx * 2, width // 2 - len(button) // 2, button)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(height // 2 + idx * 2, width // 2 - len(button) // 2, button)

        stdscr.addstr(height - 2, width // 2 - len("Use Tab to navigate, Enter to select") // 2, "Use Tab to navigate, Enter to select")
        stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    while True:
        draw_screen()
        key = stdscr.getch()

        if key == 9:  # Tab key
            current_button = (current_button + 1) % len(buttons)
        elif key in [10, 13]:  # Enter key
            if buttons[current_button] == "Quit":
                exit()
            elif buttons[current_button] == "Agree":
                stdscr.clear()
                stdscr.refresh()
                show_main_menu(stdscr)
                stdscr.clear()
                stdscr.refresh()
                curses.curs_set(1)
                current_button = 0
                break
            elif buttons[current_button] == "Configure":
                stdscr.clear()
                stdscr.refresh()
                configure_server(stdscr)
                stdscr.clear()
                stdscr.refresh()
                curses.curs_set(1)
                current_button = 0

def show_main_menu(stdscr):
    curses.curs_set(1)
    height, width = stdscr.getmaxyx()
    buttons = ["Hard Power", "Hard Restart", "Soft Restart", "Soft Power", "Quit"]
    current_button = 0
    last_action_timestamp = {
        "Hard Power": None,
        "Hard Restart": None,
        "Ping": None
    }
    ping_results = []

    def draw_screen():
        stdscr.clear()
        stdscr.addstr(0, width // 2 - len("Main Menu") // 2, "Main Menu")

        for idx, button in enumerate(buttons):
            timestamp = ""
            if button in last_action_timestamp and last_action_timestamp[button]:
                timestamp = last_action_timestamp[button].strftime(" %Y-%m-%d %H:%M:%S")
            if idx == current_button:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(height // 2 - len(buttons) + idx * 2, width // 2 - len(button) // 2, button + timestamp)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(height // 2 - len(buttons) + idx * 2, width // 2 - len(button) // 2, button + timestamp)

        if ping_results:
            stdscr.addstr(0, width - 20, "Last 10 Pings:")
            for idx, result in enumerate(ping_results[-10:]):
                stdscr.addstr(1 + idx, width - 20, result)

        stdscr.addstr(height - 2, width // 2 - len("Use Tab to navigate, Enter to select") // 2, "Use Tab to navigate, Enter to select")
        stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def automatic_ping():
        while True:
            try:
                result = subprocess.run(["ping", "-c", "1", config["ip_address"]], capture_output=True, text=True, check=True)
                response_time = result.stdout.split("time=")[-1].split(" ms")[0] + " ms"
                ping_results.append(response_time)
                if len(ping_results) > 10:
                    ping_results.pop(0)
            except subprocess.CalledProcessError:
                ping_results.append("Ping failed")
                if len(ping_results) > 10:
                    ping_results.pop(0)
            last_action_timestamp["Ping"] = datetime.datetime.now()
            draw_screen()
            time.sleep(1)

    import threading
    threading.Thread(target=automatic_ping, daemon=True).start()

    while True:
        draw_screen()
        key = stdscr.getch()

        if key == 9:  # Tab key
            current_button = (current_button + 1) % len(buttons)
        elif key in [10, 13]:  # Enter key
            if buttons[current_button] == "Quit":
                break
            elif buttons[current_button] == "Hard Power":
                confirm_action(stdscr, "Hard Power", 3, last_action_timestamp)
            elif buttons[current_button] == "Hard Restart":
                confirm_action(stdscr, "Hard Restart", 7, last_action_timestamp)
            elif buttons[current_button] == "Soft Restart":
                send_ssh_command("sudo powerdown -r")
            elif buttons[current_button] == "Soft Power":
                send_ssh_command("sudo powerdown")
     
def confirm_action(stdscr, action, pin, last_action_timestamp):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    confirmation_text = f"Are you sure you want to perform {action}?"
    stdscr.addstr(height // 2, width // 2 - len(confirmation_text) // 2, confirmation_text)
    stdscr.addstr(height // 2 + 2, width // 2 - len("Press 'y' to confirm, 'n' to cancel") // 2, "Press 'y' to confirm, 'n' to cancel")
    stdscr.refresh()
    
    key = stdscr.getch()
    if key == ord('y'):
        perform_gpio_action(pin)
        last_action_timestamp[action] = datetime.datetime.now()
    stdscr.clear()
    stdscr.refresh()

def perform_gpio_action(pin):
    wp.wiringPiSetup()
    wp.pinMode(pin, 1)
    wp.digitalWrite(pin, 1)
    time.sleep(0.5)
    wp.digitalWrite(pin, 0)

def configure_server(stdscr):
    global config

    curses.curs_set(1)
    height, width = stdscr.getmaxyx()
    fields = ["alias", "username", "ip_address"]
    buttons = ["Save", "Test Connection", "Menu"]
    current_field = 0
    current_button = -1  # -1 means no button is currently selected
    input_text = {field: config[field] for field in fields}

    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def draw_screen():
        stdscr.clear()
        stdscr.addstr(0, width // 2 - len("Server Configuration") // 2, "Server Configuration")

        for idx, field in enumerate(fields):
            stdscr.addstr(height // 2 - len(fields) + idx * 2, width // 4, field.capitalize() + ":")
            stdscr.addstr(height // 2 - len(fields) + idx * 2, width // 2, input_text[field])
            if idx == current_field and current_button == -1:
                stdscr.addstr(height // 2 - len(fields) + idx * 2, width // 2 + len(input_text[field]), "_")

        for idx, button in enumerate(buttons):
            if current_button == idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(height // 2 + len(fields) * 2 + idx * 2, width // 2 - len(button) // 2, button)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(height // 2 + len(fields) * 2 + idx * 2, width // 2 - len(button) // 2, button)

        stdscr.addstr(height - 2, width // 2 - len("Use Tab to navigate, Enter to select") // 2, "Use Tab to navigate, Enter to select")
        stdscr.refresh()

    while True:
        draw_screen()

        key = stdscr.getch()

        if key == 9:  # Tab key
            if current_button == -1:
                if current_field < len(fields) - 1:
                    current_field += 1
                else:
                    current_field = -1
                    current_button = 0
            else:
                current_button = (current_button + 1) % (len(buttons) + 1)
                if current_button == len(buttons):
                    current_button = -1
                    current_field = 0
        elif key in [10, 13]:  # Enter key
            if current_button != -1:
                if current_button == 0:  # Save
                    for field in fields:
                        config[field] = input_text[field]
                    save_config()
                    show_result(stdscr, "Configuration saved successfully")
                    current_field = 0
                    current_button = -1  # Reset focus after save
                elif current_button == 1:  # Test Connection
                    for field in fields:
                        config[field] = input_text[field]
                    test_connection(stdscr)
                    current_field = 0
                    current_button = -1  # Reset focus after test
                elif current_button == 2:  # Menu
                    for field in fields:
                        config[field] = input_text[field]
                    break
        elif key == curses.KEY_BACKSPACE or key == 127:
            if current_button == -1:
                input_text[fields[current_field]] = input_text[fields[current_field]][:-1]
        else:
            if current_button == -1:
                input_text[fields[current_field]] += chr(key)
            else:
                current_button = -1

def test_connection(stdscr):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Check if keys exist
        home_dir = os.path.expanduser('~')
        ssh_dir = os.path.join(home_dir, '.ssh')
        private_key_file = os.path.join(ssh_dir, 'id_rsa')
        public_key_file = os.path.join(ssh_dir, 'id_rsa.pub')

        if not os.path.exists(private_key_file) or not os.path.exists(public_key_file):
            os.makedirs(ssh_dir, exist_ok=True)
            os.system(f'ssh-keygen -t rsa -b 2048 -f {private_key_file} -N ""')

        # Copy public key to the server using pexpect to handle password prompt
        child = pexpect.spawn(f'ssh-copy-id -i {public_key_file} {config["username"]}@{config["ip_address"]}')
        child.interact()  # Allow user to interact directly with the process

        # Test the SSH connection
        ssh.connect(config["ip_address"], username=config["username"])
        ssh.exec_command('echo Connection successful')
        ssh.close()

        show_result(stdscr, "Connection successful")
    except paramiko.AuthenticationException:
        show_result(stdscr, "Authentication failed: Check your username and password.")
    except Exception as e:
        show_result(stdscr, f"Connection failed: {str(e)}")

def show_result(stdscr, message):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height // 2, width // 2 - len(message) // 2, message)
    stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return to the menu") // 2, "Press any key to return to the menu")
    stdscr.refresh()
    stdscr.getch()

def send_ssh_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(config["ip_address"], username=config["username"])
    ssh.exec_command(command)
    ssh.close()

def main():
    load_config()
    if config["ip_address"] == "":
        configure_server_init()
    else:
        curses.wrapper(show_warning)

if __name__ == "__main__":
    main()
