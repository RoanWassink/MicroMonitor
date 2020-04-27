import matplotlib
import psutil
import datetime
from app import app, db
from app.models import CPU, System
import socket

def cpu_percent():
    p = CPU(cpu_usage=psutil.cpu_percent(), system_id=socket.gethostname())
    db.session.add(p)
    db.session.commit()



cpu_percent()