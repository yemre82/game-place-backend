from datetime import datetime
from personel.models import ChildsOfGames
from parent.utils import sendSMSVerificationForParents
import requests
from parent.models import BalanceHistory, Bills
from parent.utils import generate_sha256_for_transactionId
import pyotp
import hashlib
import json
from personel.utils import sendSMSForParents

def sendSMSToParents():
    this_time=datetime.now()
    this_time_ts=datetime.timestamp(this_time)
    gamers=ChildsOfGames.objects.filter(ended_at__gt=this_time,is_sent_email=False,is_finished=False)
    phones=[]
    for i in gamers:
        if datetime.timestamp(i.ended_at)-this_time_ts<600:
            phones.append(i.phone)
            i.is_sent_email=True
            i.save()
    sendSMSVerificationForParents(phones)
    return True
    
    
def denemeBills():
    totp = pyotp.TOTP("JKFLSNVITJDNGVXS", digest=hashlib.sha1, interval=3600)


    url = "http://verasql.playland.com.tr:20000/referrer.integration"

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Password": "JKFLSNVITJDNGVXS",
        "OTP": str(totp.now())
    }
    
    balance_obj=BalanceHistory.objects.filter(adding_balance=True,is_gift=False)
    for i in balance_obj:
        if i.created_at.year==2022 and i.created_at.month==8 and i.created_at.day<=16:
            products_list=[]
            try:
                Bills.objects.get(invoice_date=i.created_at)
                return False
            except:
                if i.balance>=600:
                    products={
                        "stock_code":"600 TL + 250 TL OYUN BEDELİ",
                        "barcode":"600600250",
                        "count":1,
                        "price":600
                    }
                    products_list.append(products)
                    if i.balance-600>0:
                        products={
                            "stock_code":"1TL",
                            "barcode":"10010",
                            "count":i.balance-600,
                            "price":1
                        }
                        products_list.append(products)
                elif i.balance>=400 and i.balance<600:
                    products={
                        "stock_code":"400 TL + 150 TL OYUN BEDELİ",
                        "barcode":"400400150",
                        "count":1,
                        "price":400
                    }
                    products_list.append(products)
                    if i.balance-400>0:
                        products={
                            "stock_code":"1TL",
                            "barcode":"10010",
                            "count":i.balance-400,
                            "price":1
                        }
                        products_list.append(products)
                elif i.balance>=300 and i.balance<400:
                    products={
                        "stock_code":"300 TL + 80 TL OYUN BEDELİ",
                        "barcode":"30030080",
                        "count":1,
                        "price":300
                    }
                    products_list.append(products)
                    if i.balance-300>0:
                        products={
                            "stock_code":"1TL",
                            "barcode":"10010",
                            "count":i.balance-300,
                            "price":1
                        }
                        products_list.append(products)
                elif i.balance>=200 and i.balance<300:
                    products={
                        "stock_code":"200 TL + 40 TL OYUN BEDELİ",
                        "barcode":"20020040",
                        "count":1,
                        "price":200
                    }
                    products_list.append(products)
                    if i.balance-200>0:
                        products={
                            "stock_code":"1TL",
                            "barcode":"10010",
                            "count":i.balance-200,
                            "price":1
                        }
                        products_list.append(products)
                else:
                    products={
                        "stock_code":"1TL",
                        "barcode":"10010",
                        "count":i.balance,
                        "price":1
                    }
                    products_list.append(products)
                
                transaction_id=generate_sha256_for_transactionId(i.user.phone,datetime.now())
                data={
                    "Test":False,
                    "InvoiceDate":i.created_at,
                    "Host":"mobile.playland.com",
                    "BranchCode":"PLAYLAND.MOBIL",
                    "TerminalCode":"PLAYLAND142",
                    "Type":"Sale",
                    "Guid":transaction_id,
                    "Current":{
                        "phone":i.user.phone,
                        "firstname":i.user.firstname,
                        "lastname":i.user.lastname,
                        "email":i.user.email,
                        "title":i.user.firstname+" "+i.user.lastname,
                        "address":"TANIMSIZ",
                        "tax_office":"SAHIS",
                        "city":"ISTANBUL",
                        "tax_number":"11111111111",
                        "national_id":i.user.member_id
                    },
                    "Data":products_list
                }
                response = requests.post(url, headers=headers, json=data)
                response=response.json()
                
                if response["STATE"]:
                    Bills.objects.create(
                        user=i.user,
                        firstname=i.user.firstname,
                        lastname=i.user.lastname,
                        phone=i.user.phone,
                        email=i.user.email,
                        title=i.user.firstname+" "+i.user.lastname,
                        national_id=i.user.member_id,
                        guid=transaction_id,
                        invoice_date=i.created_at,
                        totp=totp.now(),
                        product_list=json.dumps(products_list, ensure_ascii=False),
                        invoince=response["INVOICE_GUID"],
                        is_approve=True,
                        price=i.balance
                    )
                else:
                    Bills.objects.create(
                        user=i.user,
                        firstname=i.user.firstname,
                        lastname=i.user.lastname,
                        phone=i.user.phone,
                        email=i.user.email,
                        title=i.user.firstname+" "+i.user.lastname,
                        national_id=i.user.member_id,
                        guid=transaction_id,
                        invoice_date=i.created_at,
                        totp=totp.now(),
                        product_list=json.dumps(products_list, ensure_ascii=False),
                        invoince=response["DESCRIPTION"],
                        price=i.balance
                    )