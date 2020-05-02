import matplotlib
import psutil
import time
import datetime
from app import app, db
from app.models import System
import socket
sampleFreq = 1*30


def main():
    while True:
        system_id = socket.gethostname()
        cpu_usage = psutil.cpu_percent(interval=1)
        #cpu_temp = psutil.sensors_temperatures()
        disk_space = psutil.disk_usage('/')
        disk_percent= disk_space.percent
        disk_free = disk_space.free
        disk_used = disk_space.used
        p = System(cpu_usage=cpu_usage, system_id=system_id, disk_percent=disk_percent, disk_free=disk_free, disk_used=disk_used)
        db.session.add(p)
        db.session.commit()
        time.sleep(sampleFreq)

main()