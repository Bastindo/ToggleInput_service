import os
import evdev
import multiprocessing
import time

FIFO = '/tmp/touchscreen.fifo'
grabbed = False

def get_touchscreen_event_id():
    with open('/proc/bus/input/devices') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if 'Name="CUST0000:00 27C6:0111"' in line:
            handlers_line = lines[i + 4]
            return handlers_line.split()[-1]

    return None

def grab_device(device_path):
    device = evdev.InputDevice(device_path)
    global grabbed
    while grabbed:
        try:
            device.grab()
            os.system("echo 1 > /tmp/touchscreen_grabbed")
        except OSError:
            pass  # device is already grabbed
        time.sleep(1)  # avoid busy looping
        command = os.read(fifo, 4096).decode('utf-8')
        if command == 'ungrab':
            print("ungrab received")
            os.system("echo 0 > /tmp/touchscreen_grabbed")
            grabbed = False
            ungrab_device(device_path)

def ungrab_device(device_path):
    device = evdev.InputDevice(device_path)
    try:
        device.ungrab()
        os.system("echo 0 > /tmp/touchscreen_grabbed")
    except OSError:
        pass  # device is already ungrabbed

def daemon(device_path):
    global grabbed
    while True:
        command = os.read(fifo, 4096).decode('utf-8')
        if command == 'grab':
            print("grab received")
            grabbed = True
            grab_device(device_path)
        elif command == 'ungrab':
            print("ungrab received")
            grabbed = False
            ungrab_device(device_path)
        else:
            print(f'Unknown command: {command}')

if __name__ == "__main__":
    device_path = f"/dev/input/{get_touchscreen_event_id()}"

    try:
        os.mkfifo(FIFO)
    except FileExistsError:
        pass  # FIFO already exists
        
    os.chmod(FIFO, 0o666)
    os.system("echo 0 > /tmp/touchscreen_grabbed")

    fifo = os.open(FIFO, os.O_RDWR)  # open the FIFO

    p = multiprocessing.Process(target=daemon, args=(device_path,))
    p.start()

    print(f"Daemon started with PID {p.pid}")

