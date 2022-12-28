import xml.etree.ElementTree as ET
import math
import random
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import time
import requests
import os

from be.responses import response_200


def sendSMSForParents(nums,text):
    data="/home/ubuntu/playland/be/be/sms_verification.xml"
    mytree = ET.parse(data)
    myroot = mytree.getroot()

    for sms_text in myroot.iter('metin'):
        sms_text.text = str(text)
    string_obj=""
    for num_text in myroot.iter('nums'):
        i=0
        for num in nums:
            i+=1
            string_obj += str(num)
            if i!=len(nums):
                string_obj+=","
    num_text.text=string_obj
    mytree.write('/home/ubuntu/playland/be/be/new2.xml')
    with open("/home/ubuntu/playland/be/be/new2.xml","rb") as file:
        data=file.readlines()
    string_asd=""
    for i in data:
        string_asd+=i.decode("utf-8")
    headers={'Content-Type':'text/xml; charset=UTF-8'}
    r=requests.post("https://smsgw.mutlucell.com/smsgw-ws/sndblkex",data=string_asd,headers=headers)
    return response_200(str(r),None)