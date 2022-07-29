import numpy as np
import cv2
import time
from switch import switch_asset
import os
from PIL import Image
from watch import Watcher,TimeLimit
import requests,json
from requests.structures import CaseInsensitiveDict
import requests
from asset import get_dict
import pymysql
from datetime import datetime
from aws_rds import get_device,get_latlng,get_rule_id,get_asset_id,get_asset,get_cam,insert_details
from flask import Flask,request
import threading
import queue
app = Flask(__name__)


fifo_queue = queue.Queue()


key=os.getenv('KEY')
w = Watcher(0)
t = TimeLimit()
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
        npimg = np.fromfile(request.files['imagedata'], np.uint8)
        a = threading.Thread(target=join, args=[data,npimg])
        a.name = "main_t"
        a.setDaemon(True)
        fifo_queue.put(a)
        a.start()
        return "200"
    else:
        return "401"

def join(data,npimg):
    vb = []
    thread_list=[thread.name for thread in threading.enumerate()]
    vb.append(thread_list)
    #print(type(thread_list))
    print(vb,"list")
    #if vb[0][1] != "main_t":
    #if len(vb[0])<=2:
    if vb[0].count("main_t") <=1 :
        print("im here.................................................................")
        #s = time.time()
        ds = threading.Thread(target=inference_thread, args=[data,npimg])
        #ds.name = "main_thrd"
        ds.setDaemon(True)
        fifo_queue.put(ds)
        ds.start()
        # e = time.time()
        # time.sleep(round(e-s,2))
        ds.join()
        
        #print("duration...........................................................",round(e-s,2))
        
        vb.clear()
    else:
        print("im out....................................................................")
        pass
    
    #vb.clear()
    print('will passed here too')



main_d={}
def inference_thread(data,npimg):
    t = TimeLimit()
    od = eval(data)
    #print(od,type(od))
    od_list = od['objDetectionList']
    camera_id = od['cameraId']
    print(camera_id)
    count = len(od_list)
    print(count)
    watch = w.variable < count
    print(watch)
    print(watch,w.variable,count)
    if count >= 1 and watch:
        try:
            if camera_id in main_d:
                cams = main_d[camera_id][0]
                device_id = cams[1]
                device_data = main_d[camera_id][1]
                latlng = main_d[camera_id][2]
                print("main_d taken")
            else:
                cams = get_cam(camera_id)
                print(cams)
                device_id = cams[1]
                device_data = get_device(device_id)
                #print(device_data)
                latlng = get_latlng(device_data[2])
                #print(latlng)
                main_d.update({camera_id:[cams,device_data,latlng]})
                print("getting from db")
            while True:
                if eval(device_data[-2]):
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
                r_id = get_rule_id(r1)
                print(r_id)
                a_id = get_asset_id(device_data[2],r_id,device_data[1],device_id)
                asset = get_asset(a_id)

                print(asset)
                print(device_data[0])
                data_dict = get_dict(device_data[0],asset)
                #print(data_dict)
                mimetype = str(data_dict['mimetype'])
                name = str(data_dict['name'])
                duration = int(data_dict['duration'])
                print(name,mimetype)
                # print("waiting time:",t.check_value())
                # if t.check_value() > duration:
                cc = threading.Thread(target = switch_asset,args = [asset,device_data[0]])
                fifo_queue.put(cc)
                cc.start()
                threading.Thread(target = insert_details,args = [device_data[2],device_data[0],name,mimetype,count,z,r1]).start()
                time.sleep(duration+1)
                #w.check_value(count)
                #return "its done"
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
