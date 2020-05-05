import socket
from threading import Thread
import psutil
import time
s=socket.socket()
sleeptime = 1*30

s=socket.socket()
s.connect(('127.0.0.1', 5001))
while True:
    system_id = socket.gethostname()
    cpu_usage = psutil.cpu_percent(interval=1)
    # cpu_temp = psutil.sensors_temperatures()
    disk_space = psutil.disk_usage('/')
    disk_percent = disk_space.percent
    disk_free = disk_space.free
    disk_used = disk_space.used
    metrics = [system_id, cpu_usage, disk_percent, disk_free, disk_used]
    data = str(metrics)
    s.send(data.encode())
    time.sleep(sleeptime)
s.close()
