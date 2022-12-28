import xml.etree.ElementTree as ET
import math
import random
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import time
import requests
import os
from be.responses import response_200

from parent.models import CustomUser


def sendSMSVerification(verification_code, nums):
    data="/home/ubuntu/be/be/sms_verification.xml"
    mytree = ET.parse(data)
    myroot = mytree.getroot()

    for sms_text in myroot.iter('metin'):
        sms_text.text = " Playland mobil uygulamasi icin onay numaraniz: "+verification_code+"."
    string_obj=""
    for num_text in myroot.iter('nums'):
        i=0
        for num in nums:
            i+=1
            string_obj += str(num)
            if i!=len(nums):
                string_obj+=","
    num_text.text=string_obj
    mytree.write('/home/ubuntu/be/be/new.xml')
    with open("/home/ubuntu/be/be/new.xml","rb") as file:
        data=file.readlines()
    string_asd=""
    for i in data:
        string_asd+=i.decode("utf-8")
    headers={'Content-Type':'text/xml; charset=UTF-8'}
    r=requests.post("https://smsgw.mutlucell.com/smsgw-ws/sndblkex",data=string_asd,headers=headers)
    return response_200(str(r),None)
    
    
    
def sendSMSVerificationForParents(nums):
    data="/home/ubuntu/be/be/sms_verification.xml"
    mytree = ET.parse(data)
    myroot = mytree.getroot()

    for sms_text in myroot.iter('metin'):
        sms_text.text = " Playland'de oynayan cocugunuzun suresi bitmek uzere. Uygulamaya girip cocugunuzun oyun suresini uzatabilir ya da cocugunuzu playland'den alabilirsiniz."
    string_obj=""
    for num_text in myroot.iter('nums'):
        i=0
        for num in nums:
            i+=1
            string_obj += str(num)
            if i!=len(nums):
                string_obj+=","
    num_text.text=string_obj
    mytree.write('/home/ubuntu/be/be/new1.xml')
    with open("/home/ubuntu/be/be/new1.xml","rb") as file:
        data=file.readlines()
    string_asd=""
    for i in data:
        string_asd+=i.decode("utf-8")
    headers={'Content-Type':'text/xml; charset=UTF-8'}
    r=requests.post("https://smsgw.mutlucell.com/smsgw-ws/sndblkex",data=string_asd,headers=headers)
    return response_200(str(r),None)
   
    

def generate_sha256(data, now):
    string = str(data)+str(now)+"playland_created_by_yemre"
    hash = hashlib.sha256(f'{string}'.encode()).hexdigest()
    return hash


def generate_random_num():
    random_str = ""
    digits = [i for i in range(0, 10)]
    for i in range(6):
        index = math.floor(random.random()*10)
        random_str += str(digits[index])
    return random_str


def phone_exist(data):
    try:
        CustomUser.objects.get(phone=data)
        return True
    except ObjectDoesNotExist as e:
        return False



def generate_sha256_for_user(data, now):
    string = str(data)+str(now)+"playland_created_by_yemre"
    hash = hashlib.sha256(f'{string}'.encode()).hexdigest()
    return hash[:8]
    
    
def generate_sha256_for_transactionId(data, now):
    string = str(data)+str(now)+"playland_created_by_yemre"
    hash = hashlib.sha256(f'{string}'.encode()).hexdigest()
    return hash[:12]