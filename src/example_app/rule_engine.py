from aws_rds import get_ruleEngine,get_latlng,get_device,get_cam,get_asset,get_rule_id
import pandas as pd
import os


def get_ruleengine_data():
    file_name = 'rule_engine.csv'
    if(os.path.exists(file_name) and os.path.isfile(file_name)):
        os.remove(file_name)
        print("file deleted")
    a=get_ruleEngine()
    df = pd.DataFrame(a,columns=['id','site_id','rule','asset','device_type','device_id'])
    #print(df)
    #outfile = open(file_name, 'w')
    df.to_csv('rule_engine.csv',index=False,header=True)
    #outfile.close()  
    print("file_created")


def get_asset_data():
    file_name = 'assets.csv'
    if(os.path.exists(file_name) and os.path.isfile(file_name)):
        os.remove(file_name)
        print("file deleted")
    a=get_asset()
    df = pd.DataFrame(a,columns=['id','asset'])
    df.to_csv('assets.csv',index=False,header=True,na_rep='Unkown',)
    print("file_created")    

def get_rule_data():
    file_name = 'rules.csv'
    if(os.path.exists(file_name) and os.path.isfile(file_name)):
        os.remove(file_name)
        print("file deleted")
    a=get_rule_id()
    df = pd.DataFrame(a,columns=['name','id'])
    df.to_csv('rules.csv',index=False,header=True)
    print("file_created")  
  

def get_latlng_data():
    file_name = 'sites.csv'
    if(os.path.exists(file_name) and os.path.isfile(file_name)):
        os.remove(file_name)
        print("file deleted")
    a=get_latlng()
    df = pd.DataFrame(a,columns=['siteId','latitude','longitude'])
    df.to_csv('sites.csv',index=False,header=True)
    print("file_created")  

def get_device_data():
    file_name = 'devices.csv'
    if(os.path.exists(file_name) and os.path.isfile(file_name)):
        os.remove(file_name)
        print("file deleted")
    a=get_device()
    df = pd.DataFrame(a,columns=['deviceId','deviceName','deviceTypeId','siteId','temp_range','age_range','Demographics','device_ip'])
    df.to_csv("devices.csv",index=False,header=True)
    print("file_created") 


def get_cam_data():
    file_name = 'camera.csv'
    if(os.path.exists(file_name) and os.path.isfile(file_name)):
        os.remove(file_name)
        print("file deleted")
    a=get_cam()
    df = pd.DataFrame(a,columns=['cameraId','deviceId','siteId','potentialId'])
    df.to_csv("camera.csv",index=False,header=True)
    print("file_created")  

get_ruleengine_data()
get_asset_data()
get_latlng_data()
get_rule_data()
get_cam_data()
get_device_data()

df = pd.read_csv('rule_engine.csv')
df1 = pd.read_csv('assets.csv',index_col ="id")
df2 = pd.read_csv('rules.csv',index_col ="name")
df3 = pd.read_csv('sites.csv',index_col ="siteId")
df4 = pd.read_csv('devices.csv', index_col = "deviceId")
df5 = pd.read_csv('camera.csv', index_col = "cameraId")


def get_asset_id(site,rule,d_type,d_id):
    db = df["asset"][(df['site_id'] == site) & (df['rule'] == rule) & (df['device_type'] == d_type) & (df['device_id'] == d_id)]
    vb = list(db)
    return vb
def get_asset(a_id):
    db = df1.loc[a_id]
    vb = list(db)
    return vb
def get_rule_id(r1):
    db = df2.loc[r1]
    vb = list(db)
    return vb
def get_latlng(site):
    db = df3.loc[site]
    vb = list(db)
    return vb
def get_device(device_id):
    db = df4.loc[device_id]
    vb = list(db)
    return vb
def get_cam(camera_id):
    db = df5.loc[camera_id]
    vb = list(db)
    return vb
