import requests
from requests.structures import CaseInsensitiveDict
import threading
import os
import dot
import time

lock = threading.Lock()

def switch_assets(_id,dev,duration):
    lock.acquire()
    Process_list=[thread.name for thread in threading.enumerate()]
    print(Process_list)
    if Process_list.count("running")==1:
        url = os.getenv("IVIS_SCREENLY_API1")+"{}".format(_id)+os.getenv("IVIS_SCREENLY_API2")+"{}".format(dev) #url = os.getenv("SCREENLY_CONTROL_API")+"asset&{}".format(_id)
        print(url)
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        resp = requests.get(url, headers=headers)
        time.sleep(duration+1)
        lock.release()
    else:
        print("its etra threads passing in inner thread")
        #resp.status_code=200
        lock.release()
        pass
    #return resp.status_code


def switch_asset(_id,dev):
    url = os.getenv("IVIS_SCREENLY_API1")+"{}".format(_id)+os.getenv("IVIS_SCREENLY_API2")+"{}".format(dev) #url = os.getenv("SCREENLY_CONTROL_API")+"asset&{}".format(_id)
    print(url)
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    resp = requests.get(url, headers=headers)
    return resp.status_code

