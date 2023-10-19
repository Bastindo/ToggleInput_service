import os
import evdev
import multiprocessing
import time

FIFO = '/tmp/touchscreen.fifo'
grabbed = False

def get_touchscreen_event_id(name):
    s = 'Name="{0}"'.format(name)
    print(s)
    with open('/proc/bus/input/devices') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if s in line:
            handlers_line = lines[i + 4]
            #t = handlers_line.split()[-1]
            words = handlers_line.split()

            for word in words:
                if word.startswith('event'):
                    eventid = word
                    break

            print(eventid)

            return eventid
    return None

def grab_device(device_path, device_path2):
    device = evdev.InputDevice(device_path)
    device2 = evdev.InputDevice(device_path2)
    global grabbed
    while grabbed:
        try:
            device.grab()
            device2.grab()
            os.system("echo 1 > /tmp/touchscreen_grabbed")
        except OSError:
            pass  # device is already grabbed
        time.sleep(1)  # avoid busy looping
        command = os.read(fifo, 4096).decode('utf-8')
        if command == 'ungrab':
            print("ungrab received")
            os.system("echo 0 > /tmp/touchscreen_grabbed")
            grabbed = False
            ungrab_device(device_path, device_path2)

def ungrab_device(device_path, device_path2):
    device = evdev.InputDevice(device_path)
    device2 = evdev.InputDevice(device_path2)
    try:
        device.ungrab()
        device2.ungrab()
        os.system("echo 0 > /tmp/touchscreen_grabbed")
    except OSError:
        pass  # device is already ungrabbed

def daemon(device_path, device_path2):
    global grabbed
    while True:
        command = os.read(fifo, 4096).decode('utf-8')
        if command == 'grab':
            print("grab received")
            grabbed = True
            grab_device(device_path, device_path2)
        elif command == 'ungrab':
            print("ungrab received")
            grabbed = False
            ungrab_device(device_path, device_path2)
        else:
            print(f'Unknown command: {command}')

if __name__ == "__main__":
    print(get_touchscreen_event_id('ELAN9009:00 04F3:2C1B'))
    device_path2 = f"/dev/input/{get_touchscreen_event_id('ELAN9009:00 04F3:2C1B')}"
    device_path = f"/dev/input/{get_touchscreen_event_id('AT Translated Set 2 keyboard')}"

    try:
        os.mkfifo(FIFO)
    except FileExistsError:
        pass  # FIFO already exists
        
    os.chmod(FIFO, 0o666)
    os.system("echo 0 > /tmp/touchscreen_grabbed")

    fifo = os.open(FIFO, os.O_RDWR)  # open the FIFO

    p = multiprocessing.Process(target=daemon, args=(device_path,device_path2,))
    #p2 = multiprocessing.Process(target=daemon, args=(device_path2,))
    p.start()
    #p2.start()

    print(f"Daemon started with PID {p.pid}")

