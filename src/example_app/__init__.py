import numpy as np
import cv2
import time
from switch import switch_asset
import os
from PIL import Image
import requests,json
from requests.structures import CaseInsensitiveDict
import requests
from asset import get_dict
from datetime import datetime
from aws_rds import insert_details
from flask import Flask,request
import threading
import queue
from rule_engine import get_asset_data,get_ruleengine_data,get_rule_data,get_latlng_data,get_device_data,get_cam_data,get_asset,get_asset_id,get_rule_id,get_latlng,get_device,get_cam
import concurrent.futures

app = Flask(__name__)

fifo_queue = queue.Queue()
key=os.getenv('KEY')
def pin(status,no,ip):
    #url = os.getenv("RPI_PINS_API")+ status
    url = 'http://'+ip+':8083/api/pins/'+status
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data = json.dumps({"pin":no})
    resp = requests.post(url, headers=headers, data=data)
    return resp.status_code



def temp(lat,lng,rng):
    day=time.strftime("%p")
    url = os.getenv('URL').format(lat,lng,key)
    try:
        c =int(float(requests.get(url).json()['current']['temp'])-273.15)
    except:
        c = 30
    if 1 <= c <= rng:
        a = 'R1'
        
    elif 1+rng <= c <= 2 * rng:
        a = 'R2'
        
    else:
        a = 'R3'
    return day+a


def sendtoserver(frame):
    imencoded = cv2.imencode(".jpg", frame)[1]
    file = {'image': ('image.jpg', imencoded.tobytes(), 'image/jpeg', {'Expires': '0'})}
    s = time.time()
    print(type(file))
    response_face = requests.post(os.getenv('MULTIFACE'), files=file, timeout=5)
    e = time.time()
    f = response_face.json()
    return f,round(e-s,2)

@app.route('/')
def sample():
    return "This application running"


    
@app.route('/ads', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        data = request.form.get('metadata', '')
        od = eval(data)
        camera_id = od['cameraId']
        npimg = np.fromfile(request.files['imagedata'], np.uint8)
        a = threading.Thread(target=join, args=[od,camera_id,npimg])
        a.name = camera_id
        a.setDaemon(True)
        fifo_queue.put(a)
        a.start()
        return "200"
    else:
        return "401"



def join(od,camera_id,npimg):
    vb = {}
    thread_list=[thread.name for thread in threading.enumerate() if thread.name == camera_id]
    vb.update({camera_id:thread_list})
    if vb[camera_id].count(camera_id) <=1:
        time.sleep(0.1)
        s = time.time()
        # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        #     future_to_url = executor.submit(inference_thread, od,npimg)
        ds = threading.Thread(target=inference_thread, args=[od,npimg])
        ds.name = "select"
        ds.setDaemon(True)
        fifo_queue.put(ds)
        ds.start()
        e = time.time()
        time.sleep(round(e-s,2))
        ds.join()
        vb[camera_id].clear()
    else:
        pass
    


asset_d={}
r_ids={}
main_d={}
def inference_thread(od,npimg):
    camera_id = od['cameraId']
    od_list = od['objDetectionList']
    count = len(od_list)
    if count >= 1:
        try:
            if camera_id in main_d:
                cams = main_d[camera_id][0]
                device_id = cams[0]
                device_data = main_d[camera_id][1]
                latlng = main_d[camera_id][2]
            else:
                cams = get_cam(camera_id)
                if len(cams)==0:
                    get_cam_data()
                    cams = get_cam(camera_id)
                device_id = cams[0]
                device_data = get_device(device_id)
                if len(device_data) == 0:
                    get_device_data()
                    device_data = get_device(device_id)
                latlng = get_latlng(device_data[2])
                if len(latlng) == 0:
                    get_latlng_data()
                    latlng = get_latlng(device_data[2])

                main_d.update({camera_id:[cams,device_data,latlng]})
            while True:
                if device_data[-2]:
                    try:
                        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                        agd,it = sendtoserver(img)
                        print("time for done image",it)
                        genders=[]
                        ages=[]
                        for i in agd:
                            genders.append(i['gender'])
                            ages.append(i['age'])
                        z = tuple(zip(genders,ages))
                        print("this is z",z)
                        g = genders.count('male') > genders.count('female')
                        #print(g)
                        ages_males = [ y for x, y in z if x  == 'male' ]
                        #print(ages_males)
                        m_classifications = [(i//device_data[-3] + 1) for i in ages_males]
                        ages_females = [ y for x, y in z if x  == 'female' ]
                        #print(ages_females)
                        f_classifications = [(i//device_data[-3] + 1) for i in ages_females]
                        if g:
                            #print('its true')
                            m = max(m_classifications,key=m_classifications.count)
                            #print(m)
                            r1=temp(latlng[0],latlng[1],device_data[3])+'MC'+str(m)
                        else:
                            #print('its false')
                            f = max(f_classifications,key=f_classifications.count)
                            r1=temp(latlng[0],latlng[1],device_data[3])+'FC'+str(f)
                    except Exception as e:
                        #return "no faces detected"
                        print("no faces detected")
                        z = None
                        r1 = temp(latlng[0],latlng[1],device_data[3])
                else:
                    z=None
                    r1 = temp(latlng[0],latlng[1],device_data[3])
                print(r1)
                if r1 in r_ids:
                    r_id = r_ids[r1]
                else:
                    r_id = get_rule_id(r1)
                    if len(r_id) == 0:
                        get_rule_data()
                        r_id = get_rule_id(r1)[0]
                    else:
                        r_id = r_id[0]
                    r_ids.update({r1:r_id})

                print(r_id)
                a_id = get_asset_id(device_data[2],r_id,device_data[1],device_id)
                if len(a_id)==0:
                    get_ruleengine_data()
                    a_id = get_asset_id(device_data[2],r_id,device_data[1],device_id)[0]
                else:
                    a_id = a_id[0]
                if a_id in asset_d:
                    asset = asset_d[a_id]
                else:
                    asset = get_asset(a_id)
                    if len(asset) == 0:
                        get_asset_data()
                        asset = get_asset(a_id)[0]
                    else:
                        asset = asset[0]
                    asset_d.update({a_id:asset})

                print(asset)
                print(device_data[0])
                data_dict = get_dict(device_data[0],asset)
                mimetype = str(data_dict['mimetype'])
                name = str(data_dict['name'])
                duration = int(data_dict['duration'])
                print(name,mimetype)
                cc = threading.Thread(target = switch_asset,args = [asset,device_data[0]])
                fifo_queue.put(cc)
                cc.start()
                time.sleep(duration+1)
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future_to_url = executor.submit(insert_details, device_data[2],device_data[0],name,mimetype,count,z,r1)
                print("its done")
                break

        except Exception as e:
            #return str(e)
            #w.check_value(0)
            print('iam here......')
            print(e)
    else:
        #w.check_value(0)
        print("no object detected")

if __name__=="__main__":
    app.run(host='0.0.0.0')

