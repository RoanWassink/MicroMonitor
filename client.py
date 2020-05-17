import socket
from threading import Thread
import psutil
import time
import platform
import datetime
def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}"
        bytes /= factor

s=socket.socket()
sleeptime = 1*30

s=socket.socket()
s.connect(('192.168.10.11',5003))
os= platform.system()
cpu_cores_phys = psutil.cpu_count(logical=False)
cpu_cores_log = psutil.cpu_count(logical=True)
cpu_freq_max = psutil.cpu_freq().max




while True:
    timestamp = datetime.datetime.now()
    svmem = psutil.virtual_memory()
    memory_total = float(get_size(svmem.total))
    memory_used = float(get_size(svmem.used))
    memory_percent = svmem.percent
    system_id = socket.gethostname()
    cpu_usage = psutil.cpu_percent(interval=1)
    # cpu_temp = psutil.sensors_temperatures()
    disk_space = psutil.disk_usage('/')
    disk_percent = disk_space.percent
    disk_free = disk_space.free
    disk_used = disk_space.used
    metrics = [system_id, cpu_usage, disk_percent, disk_free, disk_used, os, cpu_cores_phys, cpu_freq_max, memory_total, memory_used, memory_percent]
    data = str(metrics)
    s.send(data.encode())
    time.sleep(sleeptime)
s.close()
