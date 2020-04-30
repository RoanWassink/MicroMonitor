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
        cpu_usage = psutil.cpu_percent()
        p = System(cpu_usage=cpu_usage, system_id=system_id)
        db.session.add(p)
        db.session.commit()
        time.sleep(sampleFreq)

main()