import os
import pymysql
import dot
from datetime import datetime
import threading

rds_host = os.getenv('RDS_URL')
rds_user = os.getenv('RDS_USER')
rds_pass = os.getenv('RDS_PASS')
rds_db = os.getenv('RDS_DB')
rds_port = 3306

conn = pymysql.connect(host= rds_host, port = rds_port, user = rds_user, password = rds_pass,db = rds_db)
cur=conn.cursor()



def get_cam():
    conn.ping(reconnect = True)
    cmd = 'select cameraId,deviceId,siteId,potentialId from camera_devices'
    cur.execute(cmd)
    details = cur.fetchall()
    return details  


def get_device():
    conn.ping(reconnect = True)
    cmd = 'select deviceId,deviceName,deviceTypeId,siteId,temp_range,age_range,Demographics,device_ip from devices'
    cur.execute(cmd)
    details = cur.fetchall()
    return details


def get_latlng():
    conn.ping(reconnect = True)
    cmd = 'select siteId,latitude,longitude from sites'
    cur.execute(cmd)
    details = cur.fetchall()
    return details    

def get_rule_id():
    conn.ping(reconnect = True)
    cmd = 'select name,id from rules'
    cur.execute(cmd)
    details = cur.fetchall()
    return details  

def get_asset():
    conn.ping(reconnect = True)
    cmd = 'select * from assets'
    cur.execute(cmd)
    details = cur.fetchall()
    return details   

def insert_details(site,device_id,name,mimetype,count,gender_age,rule):
    conn.ping(reconnect = True)
    timestamp = datetime.now()
    cur.execute("INSERT INTO AV_raw_data(site_id,device,name,mimetype,count,gender_age,timestamp,rule) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(site,device_id,name,mimetype,count,str(gender_age),str(timestamp),rule))
    conn.commit()
    return details  

def get_ruleEngine():
    conn.ping(reconnect = True)
    cur.execute("select * from rule_engine")
    rule_data = cur.fetchall()
    return rule_data
