import threading

class SpwEvent(object):
    _events = {} 
    
    def __init__(self):
        for i in dir(self):
            if not (i.startswith('_') or i == 'set_event'):
                #print i
                x = self.__getattribute__(i)
                self._events[x] = i
                self.__setattr__(i, threading.Event())

    def set_event(self, event_id):
        self.__getattribute__(self._events[event_id]).set()
        

class SpwEvents(SpwEvent):
    _unused,\
    DpuInitialized,\
    SoCWRxDone,\
    SoCWTxDone,\
    NandDone,\
    NandFsMounted,\
    Rfpga1Configured,\
    Rfpga2Configured,\
    PreprocDone = range(9)
