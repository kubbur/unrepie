# Unrepie

Unrepie is a Flask application to manage multiple SSH command executors, each with its own configuration.

## Version

1.0

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/unrepie.git
    cd unrepie
    ```

2. Run the setup script:

    ```sh
    chmod +x setup.sh
    ./setup.sh
    ```

3. Run the application:

    ```sh
    ./unrepie
    ```

4. Open your browser and navigate to `http://localhost:5000` to access the central management interface.

## Adding Unrepie to Startup

### For Systemd (Linux)

1. Create a systemd service file:

    ```sh
    sudo nano /etc/systemd/system/unrepie.service
    ```

2. Add the following content:

    ```ini
    [Unit]
    Description=Unrepie Service
    After=network.target

    [Service]
    ExecStart=/path/to/unrepie/unrepie
    WorkingDirectory=/path/to/unrepie
    User=yourusername
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

    Replace `/path/to/unrepie` with the actual path to the Unrepie directory and `yourusername` with your username.

3. Enable and start the service:

    ```sh
    sudo systemctl enable unrepie
    sudo systemctl start unrepie
    ```

## Dependencies

- Flask
- paramiko
- ping3
