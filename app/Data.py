import socket
import select
from operator import itemgetter
from app import app, db
from app.models import System
session = db.session()
with socket.socket() as server:
    server.bind(('192.168.10.11',5003))
    server.listen(50)
    to_read = [server]  # add server to list of readable sockets.
    clients = {}
    while True:
        # check for a connection to the server or data ready from clients.
        # readers will be empty on timeout.
        readers,_,_ = select.select(to_read,[],[],0.5)
        for reader in readers:
            if reader is server:
                client,address = reader.accept()
                #print('connected',address)
                clients[client] = address # store address of client in dict
                to_read.append(client) # add client to list of readable sockets
            else:
                # Simplified, really need a message protocol here.
                data = reader.recv(4096)
                data = data.decode('utf-8')
                if not data: # No data indicates disconnect
                    #print('disconnected',clients[reader])
                    to_read.remove(reader) # remove from monitoring
                    del clients[reader] # remove from dict as well
                else:
                    #print(data)
                    data = data.strip('][').split(', ')
                    system_id, cpu_usage, disk_percent, disk_free, disk_used, os, cpu_cores_phys, cpu_freq_max, memory_total, memory_used, memory_percent = data
                    system_id=system_id.replace("'", "")
                    print(system_id)
                    p = System(os=os,cpu_usage=cpu_usage, system_id=system_id, disk_percent=disk_percent, disk_free=disk_free,
                               disk_used=disk_used, cpu_cores_phys=cpu_cores_phys, cpu_freq_max=cpu_freq_max, memory_total=memory_total, memory_used=memory_used, memory_percent=memory_percent)
                    print(cpu_cores_phys)
                    db.session.add(p)
                    db.session.commit()
        print('.',flush=True,end='')
