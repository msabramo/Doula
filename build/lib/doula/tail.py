from strap import process
import gevent

process = reload(process)

class GreenProcess(process.Process):
    sleep = staticmethod(gevent.sleep)
    
