from datetime import datetime, timedelta, date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from be.is_verified import is_verified
from be.responses import response_200, response_400
from parent.models import BalanceHistory, CustomUser, Family, Game, OTPChangePhone, OTPPhone, OTPPhoneForgot,OTPGetChild, Bills, jetonHistory, PNRTransactions
from parent.utils import generate_random_num, generate_sha256, generate_sha256_for_user, phone_exist, sendSMSVerification, generate_sha256_for_transactionId
from superuser.models import News, Branchs
from personel.models import ChildsOfGames
from parent.models import jeton, min_withdrawal_amount
import requests
import json
import iyzipay
import pyotp
import hashlib
# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def create_otp(request):
    now_2_min = datetime.now() - timedelta(minutes=2)
    phone = request.data.get("phone")
    if is_verified(phone):
        return response_400("the user is already verify phone number")
    try:
        OTPPhone.objects.get(phone=phone, created_at__gt=now_2_min)
        return response_400("The user is already")
    except ObjectDoesNotExist as e:
        otp = generate_random_num()
        description = "verification"
        OTPPhone.objects.create(
            phone=phone,
            otp=otp,
            description=description
        )
        sendSMSVerification(otp,[phone])
        return response_200("success", None)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    now_2_min = datetime.now() - timedelta(minutes=2)
    phone = request.data.get("phone")
    try:
        user_obj=CustomUser.objects.get(phone=phone)
    except ObjectDoesNotExist as e:
        return response_400("there is no such user")
    try:
        OTPPhoneForgot.objects.get(user=user_obj,phone=phone,created_at__gt=now_2_min)
        return response_400("The user is already")
    except ObjectDoesNotExist as e:
        otp = generate_random_num()
        description = "forgot password"
        OTPPhoneForgot.objects.create(
            user=user_obj,
            phone=phone,
            otp=otp,
            description=description
        )
        sendSMSVerification(otp,[phone])
        return response_200("success",None)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_forgot_password(request):
    phone = request.data.get("phone")
    try:
        user_obj=CustomUser.objects.get(phone=phone)
    except ObjectDoesNotExist as e:
        return response_400("there is no such user")
    otp_obj = OTPPhoneForgot.objects.filter(user=user_obj,phone=phone, is_verified=False).order_by('-id')[:1]
    if len(otp_obj) == 0:
        return response_400("there is no such otp")
    otp = request.data.get("otp")
    for i in otp_obj:
        if i.otp == otp:
            i.is_verified = True
            i.save()
            return response_200("success", None)
    return response_400("there is no such otp")
            
            
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_change_password(request):
    phone = request.data.get("phone")
    try:
        user_obj=CustomUser.objects.get(phone=phone)
    except ObjectDoesNotExist as e:
        return response_400("there is no such user")
    otp_obj = OTPPhoneForgot.objects.filter(user=user_obj,
        phone=phone, is_verified=True).order_by('-id')[:1]
    if len(otp_obj) == 0:
        return response_400("there is no such otp")
    password = request.data.get("password")
    password_a = request.data.get("password_again")
    if len(password) < 8:
        return response_400("the password must be 8 digit")
    if password != password_a:
        return response_400("the passwords are not match")
    user_obj.set_password(password)
    user_obj.save()
    return response_200("success", None)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    phone = request.data.get("phone")
    otp_obj = OTPPhone.objects.filter(
        phone=phone, is_verified=False).order_by('-id')[:1]
    if len(otp_obj) == 0:
        return response_400("there is no such otp")
    otp = request.data.get("otp")
    for i in otp_obj:
        if i.otp == otp:
            i.is_verified = True
            i.save()
            return response_200("success", None)
    return response_400("there is no such otp")


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    now = datetime.now()
    phone = request.data.get("phone")
    if not is_verified(phone):
        return response_400("the user is not verified")
    if phone_exist(phone):
        return response_400("this phone is already exist")
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    if now.year - birthday.year < 12:
        return response_400("the user can't this birthday")
    password = request.data.get("password")
    password_a = request.data.get("password_again")
    if len(password) < 8:
        return response_400("the password must be 8 digit")
    if password != password_a:
        return response_400("the passwords are not match")
    username = phone
    is_male = request.data.get("is_male")
    member_id=generate_sha256_for_user(phone,datetime.now())
    user_obj = CustomUser.objects.create(
        phone=phone,
        firstname=firstname,
        lastname=lastname,
        birthday=birthday,
        username=username,
        member_id=member_id,
        balance=0
    )
    user_obj.set_password(password)
    user_obj.save()
    Family.objects.create(
        parent=user_obj,
        firstname=firstname,
        lastname=lastname,
        birthday=birthday,
        is_parent=True,
        is_male=is_male,
        phone=phone
    )
    return response_200("success", None)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    phone = request.data.get("phone")
    if not is_verified(phone):
        return response_400("the user is not verified")
    if not phone_exist(phone):
        return response_400("this phone is not exist")
    try:
        user_obj = CustomUser.objects.get(phone=phone)
    except ObjectDoesNotExist as e:
        return response_400("there is no such user")
    password = request.data.get("password")
    if not user_obj.check_password(password):
        return response_400("the password is not true")
    token, _ = Token.objects.get_or_create(user=user_obj)
    return_obj = {
        "token": token.key
    }
    return response_200("success", return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_news(request):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    news_obj = News.objects.all().order_by('-id')[:20]
    news_list = []
    for news in news_obj:
        return_obj = {
            "id":news.id,
            "title": news.title,
            "short_description": news.short_description,
            "description": news.description,
            "image": "/media/"+str(news.image),
            "created_at":news.created_at,
            "is_campaign":news.is_campaign,
	    "campaign_price": news.campaign_price
        }
        news_list.append(return_obj)
    return response_200("success", news_list)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_news(request,news_id):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    try:
        news_obj=News.objects.get(id=news_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such news")
    return_obj={
        "id":news_obj.id,
        "title":news_obj.title,
        "short_description":news_obj.short_description,
        "description":news_obj.description,
        "image":"/media/"+str(news_obj.image),
        "created_at":news_obj.created_at,
        "campaign_price": news_obj.campaign_price,
	"is_campaign":news_obj.is_campaign
    }
    return response_200("success",return_obj)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_family(request):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    family_obj = Family.objects.filter(parent=request.user)
    family_list = []
    for family in family_obj:
        birthday_day=str((family.birthday).day)
        if len(birthday_day)==1:
            birthday_day="0"+birthday_day
        birthday_month=str((family.birthday).month)
        if len(birthday_month)==1:
            birthday_month="0"+birthday_month
        return_obj = {
            "id": family.id,
            "name": family.firstname,
            "surname": family.lastname,
            "birthday":birthday_day+"."+birthday_month+"."+str((family.birthday).year) ,
            "is_male":family.is_male,
            "is_parent": family.is_parent,
            "phone":family.phone,
            "profile_image":"/media/"+str(family.profile_image)
        }
        family_list.append(return_obj)
    return response_200("success", family_list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_child_to_family(request):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    is_male = request.data.get("is_male")
    if is_male=="True" or is_male=="true" or is_male==True:
        is_male=True
    else:
        is_male=False
    profile_image=request.data.get("profile_image")
    if profile_image==None:
        return response_400("invalid profile image")
    Family.objects.create(
        parent=request.user,
        firstname=firstname,
        lastname=lastname,
        birthday=birthday,
        is_male=is_male,
        profile_image=profile_image
    )
    return response_200("success", None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_adult_to_family(request):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    is_male = request.data.get("is_male")
    phone=request.data.get("phone")
    if len(phone)==0:
        return response_400("the phone must be at least 1 letter")
    try:
        Family.objects.get(phone=phone)
    except ObjectDoesNotExist as e:
        return response_400("phone number is already exist")
    Family.objects.create(
        parent=request.user,
        firstname=firstname,
        lastname=lastname,
        birthday=birthday,
        is_male=is_male,
        phone=phone,
        is_parent=True
    )
    return response_200("success",None)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_member_from_family(request):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    family_id = request.data.get("id")
    try:
        family_obj = Family.objects.get(id=family_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such family")
    if family_obj.parent != request.user:
        return response_400("you can't remove this family")
    if family_obj.phone==request.user.phone:
        return response_400("you can't remove yourself")
    family_obj.delete()
    return response_200("success", None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_member_from_family(request):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    family_id = request.data.get("id")
    try:
        family_obj = Family.objects.get(id=family_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such family")
    if family_obj.parent != request.user:
        return response_400("you can't edit this family")
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    is_male = request.data.get("is_male")
    phone=request.data.get("phone")
    is_parent=False
    if len(phone)==0:
        is_parent=True
    family_obj.firstname=firstname
    family_obj.lastname=lastname
    family_obj.birthday=birthday
    family_obj.is_male=is_male
    family_obj.phone=phone
    family_obj.is_parent=is_parent
    family_obj.save()
    return response_200("success",None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    try:
        family_obj=Family.objects.get(
            parent=request.user,
            phone=request.user.phone
        )
    except ObjectDoesNotExist as e:
        return response_400("there is no such family")
    birthday_day=str((request.user.birthday).day)
    if len(birthday_day)==1:
        birthday_day="0"+birthday_day
    birthday_month=str((request.user.birthday).month)
    if len(birthday_month)==1:
        birthday_month="0"+birthday_month
    return_obj={
        "id":request.user.id,
        "phone":request.user.phone,
        "birthday":birthday_day+"."+birthday_month+"."+str((request.user.birthday).year),
        "firstname":request.user.firstname,
        "lastname":request.user.lastname,
        "is_male":family_obj.is_male
    }

    return response_200("success",return_obj)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_name_surname(request):
    firstname=request.data.get("firstname")
    lastname=request.data.get("lastname")
    if len(firstname)==0:
        return response_400("the firstname must be at least 1 letter")
    if len(lastname)==0:
        return response_400("the lastname must be at least 1 letter")
    request.user.firstname=firstname
    request.user.lastname=lastname
    request.user.save()
    try:
        family_obj=Family.objects.get(parent=request.user,phone=request.user.phone)
    except ObjectDoesNotExist as e:
        return response_400("there is no such family")
    family_obj.firstname=firstname
    family_obj.lastname=lastname
    family_obj.save()
    return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_birthday(request):
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    try:
        family_obj=Family.objects.get(
            parent=request.user,
            firstname=request.user.firstname,
            lastname=request.user.lastname,
            phone=request.user.phone
        )
    except ObjectDoesNotExist as e:
        return response_400("family object is not valid")
    request.user.birthday=birthday
    request.user.save()
    family_obj.birthday=birthday
    family_obj.save()

    return response_200("success",None)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_phone(request):
    phone=request.data.get("phone")
    otp = generate_random_num()
    description = "verification"
    OTPChangePhone.objects.create(
        user=request.user,
        phone=phone,
        otp=otp,
        description=description
    )
    sendSMSVerification(otp,[phone])
    return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_phone_verification(request):
    change_phone_obj=OTPChangePhone.objects.filter(user=request.user).order_by("-id")[:1]
    otp=request.data.get("otp")
    for i in change_phone_obj:
        if i.otp!=otp:
            return response_400("otp is not match")
        try:
            family_obj=Family.objects.get(
                parent=request.user,
                firstname=request.user.firstname,
                lastname=request.user.lastname,
                phone=request.user.phone
            )
        except ObjectDoesNotExist as e:
            return response_400("family object is not valid")
        request.user.phone=i.phone
        request.user.save()
        family_obj.phone=i.phone
        family_obj.save()
        OTPPhone.objects.create(
            phone=i.phone,
            otp=otp,
            description="change phone",
            is_verified=True
        )
        return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password=request.data.get("old_password")
    if not request.user.check_password(old_password):
        return response_400("Eski şifreniz doğru değil.")
    password = request.data.get("password")
    password_a = request.data.get("password_again")
    if len(password) < 8:
        return response_400("Şifreniz en az 8 haneli olmak zorundadır.")
    if password != password_a:
        return response_400("Gönderdiğiniz şifreler birbirleri ile aynı değiller.")
    request.user.set_password(password)
    request.user.save()
    return response_200("success",None)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    return_obj = {
        "balance": request.user.balance
    }
    return response_200("success", return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance_history(request,filter_type):
    this_time=datetime.timestamp(datetime.now())
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    if filter_type=="24s":
        filter_time=this_time-86400
    elif filter_type=="7g":
        filter_time=this_time-604800
    elif filter_type=="30g":
        filter_time=this_time-2592000
    filter_time=datetime.fromtimestamp(filter_time)
    history_obj = BalanceHistory.objects.filter(
        user=request.user,created_at__gt=filter_time).order_by('-created_at')
    history_list = []
    
    for i in history_obj:
        return_obj = {
            "user": i.user.firstname+" "+i.user.lastname,
            "history": i.balance,
            "adding_balance": i.adding_balance,
            "city": i.city,
            "branch": i.branch,
            "game_name": i.game_name,
            "is_pnr":i.is_pnr,
            "created_at": i.created_at,
            "update_at": i.update_at
        }
        history_list.append(return_obj)
    return response_200("success", history_list)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_child_in_game(request):
    this_time=datetime.now()
    game_obj=Game.objects.filter(user=request.user,started_at__lt=this_time,ended_at__gt=this_time).order_by("-id")
    returning_list=[]
    
    for i in game_obj:
        remaining_time_ts=datetime.timestamp(i.ended_at)-datetime.timestamp(this_time)
        how_much_ticket_played=(datetime.timestamp(i.ended_at)-datetime.timestamp(i.started_at))/1800
        one_ticket_price=(i.price)/how_much_ticket_played
        return_obj={
            "game_id":i.id,
            "user":i.user.firstname + " "+ i.user.lastname,
            "gamer":i.gamer.firstname+ " "+ i.gamer.lastname,
            "gamer_id":i.gamer.id,
            "price":one_ticket_price,
            "started_at":i.started_at,
            "ended_at":i.ended_at,
            "created_at":i.created_at,
            "update_at":i.update_at,
            "remaining_time":remaining_time_ts,
            "city":i.city,
            "branch":i.branch,
            "game_name":i.game_name
        }
        returning_list.append(return_obj)
    return response_200("success",returning_list)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_child_from_game(request):
    this_time=datetime.now()
    game_obj=Game.objects.filter(user=request.user,started_at__gl=this_time,ended_at__gt=this_time).order_by("-id")
    if len(game_obj)==0:
        return response_400("the user has no child in game")
    game_id=request.data.get("game_id")
    try:
        game_obj=Game.objects.get(user=request.user,started_at__gt=this_time,ended_at__lt=this_time,id=game_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such game")
    otp = generate_random_num()
    description="get-child"
    OTPGetChild.objects.create(
        user=request.user,
        phone=request.user.phone,
        otp=otp,
        description=description,
    )
    sendSMSVerification(otp,[request.user.phone])
    return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extend_child_in_game(request):
    try:
        jeton_obj = jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        jeton_obj = jeton.objects.create(
            user=request.user
        )
    try:
        min_amount_obj = min_withdrawal_amount.objects.get(id=1)
    except:
        return response_400("there is no such id")
    this_time=datetime.now()
    game_obj=Game.objects.filter(user=request.user,started_at__lt=this_time,ended_at__gt=this_time).order_by("-id")
    if len(game_obj)==0:
        return response_400("the user has no child in game")
    game_id=request.data.get("game_id")
    try:
        game_obj=Game.objects.get(user=request.user,started_at__lt=this_time,ended_at__gt=this_time,id=game_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such game")
    how_much_ticket_played=(datetime.timestamp(game_obj.ended_at)-datetime.timestamp(game_obj.started_at))/1800
    one_ticket_price=(game_obj.price)/how_much_ticket_played
    ticket=int(request.data.get("ticket"))
    if request.user.balance<(one_ticket_price*ticket):
        return response_400("the balance is not enough")
    try:
        game_obj2=ChildsOfGames.objects.get(parent_name=request.user.firstname,parent_surname=request.user.lastname,phone=request.user.phone,branch=game_obj.branch,child_name=game_obj.gamer.firstname,child_surname=game_obj.gamer.lastname,started_at=game_obj.started_at,ended_at=game_obj.ended_at)
    except ObjectDoesNotExist as e:
        return response_400("there is no such gameobj")
    game_obj.ended_at=datetime.fromtimestamp(datetime.timestamp(game_obj.ended_at)+(ticket*1800))
    game_obj.price=game_obj.price+(one_ticket_price*ticket)
    game_obj.is_finished=False
    game_obj.save()
    game_obj2.ended_at=datetime.fromtimestamp(datetime.timestamp(game_obj.ended_at)+(ticket*1800))
    game_obj2.price=game_obj.price+(one_ticket_price*ticket)
    game_obj2.is_finished=False
    game_obj2.is_sent_email=False
    game_obj2.save()
    request.user.balance-=(one_ticket_price*ticket)
    request.user.save()
    BalanceHistory.objects.create(
        user=request.user,
        balance=(one_ticket_price*ticket),
        adding_balance=False,
        city=None,
        branch=game_obj.branch,
        game_name=game_obj.game_name,
    )
    jeton_obj.balance += (float((one_ticket_price*ticket))*float(min_amount_obj.percentage))/float(100)
    jeton_obj.save()
    jetonHistory.objects.create(
        user=request.user,
        balance=(float((one_ticket_price*ticket))*float(min_amount_obj.percentage))/float(100),
        adding_balance=True,
        city=None,
        branch=game_obj.branch,
        game_name=game_obj.game_name
    )
    return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_balance(request):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    adding_balance = request.data.get("adding_balance")
    if adding_balance <= 0:
        return response_400("balance is not being negative")
    now = request.data.get("datetime")
    sha256_proof = request.data.get("sha256_proof")
    if sha256_proof != generate_sha256(adding_balance, now):
        return response_400("sha256 proof is not match")
    BalanceHistory.objects.create(
        user=request.user,
        balance=adding_balance,
        adding_balance=True
    )
    gift=0
    if adding_balance>500:
        gift=300 
    elif adding_balance>250 and adding_balance<500:
        gift=125
    elif adding_balance>150 and adding_balance<250:
        gift=60
    BalanceHistory.objects.create(
        user=request.user,
        balance=gift,
        adding_balance=True,
        is_gift=True
    )
    request.user.balance += (adding_balance+gift)
    request.user.save()
    return response_200("success", None)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_info(request,code):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    transaction_id=generate_sha256_for_transactionId(request.user.phone,datetime.now())
    my_obj={
        "machineCode":str(code),
        "memberId":str(request.user.member_id),
        "transactionId":str(transaction_id)
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    x = requests.post("https://api.playland.sade.io/Device/GetPrice", headers=headers, data = json.dumps(my_obj))
    response_obj=x.json()
    if response_obj["status"]==False:
        return response_400("the machine has an error")
    for_child=False
    is_money_enough=True
    if response_obj["machineType"]=="SOFT PLAY2":
        for_child=True
    if request.user.balance<response_obj["price"]:
        is_money_enough=False
    if response_obj["price"]==0:
        return response_400("this machine for personels")
    
    return_obj={
        "machine_type":response_obj["machineType"],
        "machine_name":response_obj["machineName"],
        "price":response_obj["price"],
        "for_child":for_child,
        "is_money_enough":is_money_enough,
        "your_price":request.user.balance,
        "machine_store": response_obj["machineStore"]
    }
    return response_200("success",return_obj)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def play_game(request,code):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    try:
        jeton_obj = jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        jeton_obj = jeton.objects.create(
            user=request.user
        )
    try:
        min_amount_obj = min_withdrawal_amount.objects.get(id=1)
    except:
        return response_400("there is no such id")
    transaction_id=generate_sha256_for_transactionId(request.user.phone,datetime.now())
    my_obj={
        "machineCode":str(code),
        "memberId":str(request.user.member_id),
        "transactionId":str(transaction_id)
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    x = requests.post("https://api.playland.sade.io/Device/GetPrice", headers=headers, data = json.dumps(my_obj))
    response_obj=x.json()
    if response_obj["status"]==False:
        return response_400("the machine has an error")
    if response_obj["price"]==0:
        return response_400("this machine for personels")
    if response_obj["machineType"]=="SOFT PLAY2":
        if "family_id" not in request.data:
            return response_400("bad request")
        try:
            Family.objects.get(parent=request.user,is_parent=True)
        except ObjectDoesNotExist as e:
            return response_400("you are not a parent")
        family_id=request.data.get("family_id")
        try:
            family_child=Family.objects.get(parent=request.user,id=family_id)
        except ObjectDoesNotExist as e:
            return response_400("there is no such family")
        this_time_year=(datetime.now()).year
        if this_time_year-(family_child.birthday).year>12:
            return response_400("the child's age is greater than 12")
        if request.user.balance<response_obj["price"]:
            return response_400("the balance is not enough")
        if "30 dk" in str(response_obj["machineName"]):
            adding_time=1800
        elif "20 dk" in str(response_obj["machineName"]):
            adding_time=1200
        elif "40 dk" in str(response_obj["machineName"]):
            adding_time=2400
        elif "45 dk" in str(response_obj["machineName"]):
            adding_time=2700
        elif "60 dk" in str(response_obj["machineName"]):
            adding_time=3600
        elif "90 dk" in str(response_obj["machineName"]):
            adding_time=5400
        elif "120 dk" in str(response_obj["machineName"]):
            adding_time=7200 
        elif "TOP HAVUZU MOBIL TEST" in str(response_obj["machineName"]):
            adding_time=1800
        else:
            return response_400("unsupported ticket")
        started_at_ts=datetime.timestamp(datetime.now())
        ended_at_ts=started_at_ts+adding_time
        member_balance=request.user.balance
        if member_balance>=500:
            member_balance=499.0
        my_obj={
            "machineCode":str(code),
            "memberId":str(request.user.member_id),
            "transactionId":str(transaction_id),
            "memberBalance":member_balance
        }
        headers = {"Content-Type": "application/json; charset=utf-8"}
        x = requests.post("https://api.playland.sade.io/Device/StartGame", headers=headers, data = json.dumps(my_obj))
        response_obj2=x.json()
        if response_obj2["status"]==True:
            BalanceHistory.objects.create(
              user=request.user,
              balance=response_obj["price"],
              adding_balance=False,
              city=None,
              branch=response_obj["machineStore"],
              game_name=response_obj["machineName"]
            )
            request.user.balance-=(response_obj["price"])
            request.user.save()
            Game.objects.create(
                user=request.user,
                gamer=family_child,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(started_at_ts),
                ended_at=datetime.fromtimestamp(ended_at_ts),
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
            )
            ChildsOfGames.objects.create(
                parent_name=request.user.firstname,
                parent_surname=request.user.lastname,
                phone=request.user.phone,
                child_name=family_child.firstname,
                child_surname=family_child.lastname,
                is_male=family_child.is_male,
                birthday=family_child.birthday,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(started_at_ts),
                ended_at=datetime.fromtimestamp(ended_at_ts),
                is_sent_email=False,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                profile_image=family_child.profile_image
            )
            jeton_obj.balance += (float(response_obj["price"])*float(min_amount_obj.percentage))/float(100)
            jeton_obj.save()
            jetonHistory.objects.create(
                user=request.user,
                balance=(float(response_obj["price"])*float(min_amount_obj.percentage))/float(100),
                adding_balance=True,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            return response_200("success",response_obj2)
        else:
            return response_400("the game not available")
    else:
        try:
            family_parent=Family.objects.get(parent=request.user,is_parent=True)
        except ObjectDoesNotExist as e:
            return response_400("you are not a parent")
        if request.user.balance<response_obj["price"]:
            return response_400("the balance is not enough")
        started_at_ts=datetime.timestamp(datetime.now())
        member_balance=request.user.balance
        if member_balance>=500:
            member_balance=499.0
        my_obj={
            "machineCode":str(code),
            "memberId":str(request.user.member_id),
            "transactionId":str(transaction_id),
            "memberBalance":member_balance
        }
        headers = {"Content-Type": "application/json; charset=utf-8"}
        x = requests.post("https://api.playland.sade.io/Device/StartGame", headers=headers, data = json.dumps(my_obj))
        response_obj3=x.json()
        if str(response_obj3["status"])=="True":
            BalanceHistory.objects.create(
                user=request.user,
                balance=response_obj["price"],
                adding_balance=False,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            request.user.balance-=response_obj["price"]
            request.user.save()
            Game.objects.create(
                user=request.user,
                gamer=family_parent,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(started_at_ts),
                ended_at=None,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                is_finished=True
            )
            ChildsOfGames.objects.create(
                parent_name=request.user.firstname,
                parent_surname=request.user.lastname,
                phone=request.user.phone,
                child_name=family_parent.firstname,
                child_surname=family_parent.lastname,
                is_male=family_parent.is_male,
                birthday=family_parent.birthday,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(started_at_ts),
                ended_at=None,
                is_sent_email=False,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                is_finished=True
            )
            jeton_obj.balance += (float(response_obj["price"])*float(min_amount_obj.percentage))/float(100)
            jeton_obj.save()
            jetonHistory.objects.create(
                user=request.user,
                balance=(float(response_obj["price"])*float(min_amount_obj.percentage))/float(100),
                adding_balance=True,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            return response_200("success",response_obj3)
        else:
            return response_400(response_obj3)
            
            
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def iyiziPay(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    if request.user.email=="" or request.user.email==None:
        return response_400("email girilmemiş")
    email=request.user.email
    city="Istanbul"
    country="Turkiye"
    zipcode="34000"
    price=request.data.get("price")
    card_holder_name=request.data.get("card_holder_name")
    card_number=request.data.get("card_number")
    expireMonth=request.data.get("expireMonth")
    expireYear=request.data.get("expireYear")
    cvc=request.data.get("cvc")
    
    pnr_obj=PNRTransactions.objects.filter(user=request.user,transaction_type="ORAN",is_used=False).order_by('-id')
    if len(pnr_obj)!=0:
        indirim=pnr_obj[0].balance
    else:
        indirim="yok"
    options = {
        'api_key': 'aYIyCJsmt8ZuG6fyN4toZed2fqtRiqln',
        'secret_key': 'VJwmEm8S0DfUUGprn4zlsm6Nq4S9LNdi',
        'base_url': "api.iyzipay.com"
    }
    payment_card = {
        'cardHolderName': card_holder_name,
        'cardNumber': card_number,
        'expireMonth': expireMonth,
        'expireYear': expireYear,
        'cvc': cvc,
        'registerCard': '0'
    }
    buyer = {
        'id': request.user.id,
        'name': request.user.firstname,
        'surname': request.user.lastname,
        'gsmNumber': '+'+request.user.phone,
        'email': email,
        'identityNumber': "11111111111",
        'lastLoginDate': str(datetime.now()),
        'registrationDate': str(datetime.now()),
        'registrationAddress': "Istanbul",
        'ip': ip,
        'city': city,
        'country': country,
        'zipCode': zipcode
    }
    address = {
        'contactName': request.user.firstname +" "+request.user.lastname,
        'city': city,
        'country': country,
        'address': "Istanbul",
        'zipCode': zipcode
    }
    if indirim=="yok":
        basket_items = [
            {
                "id": "bakiye"+str(price),
                "price": str(price),
                "name": "bakiye"+str(price),
                "category1": "bakiye",
                "itemType": "VIRTUAL"
            }
        ]
        request1 = {
            'locale': 'tr',
            'conversationId': "bakiye"+str(price),
            'price': str(price),
            'paidPrice': str(price),
            'currency': 'TRY',
            'installment': '1',
            'basketId': "bakiye"+str(price),
            'paymentChannel': 'WEB',
            'paymentGroup': 'OTHER',
            'paymentCard': payment_card,
            'buyer': buyer,
            'shippingAddress': address,
            'billingAddress': address,
            'basketItems': basket_items
        }
    else:
        basket_items = [
            {
                "id": "bakiye"+str(price-(price*indirim)/100.0),
                "price": str(price-(price*indirim)/100.0),
                "name": "bakiye"+str(price-(price*indirim)/100.0),
                "category1": "bakiye",
                "itemType": "VIRTUAL"
            }
        ]
        request1 = {
            'locale': 'tr',
            'conversationId': "bakiye"+str(price-(price*indirim)/100.0),
            'price': str(price-(price*indirim)/100.0),
            'paidPrice': str(price-(price*indirim)/100.0),
            'currency': 'TRY',
            'installment': '1',
            'basketId': "bakiye"+str(price-(price*indirim)/100.0),
            'paymentChannel': 'WEB',
            'paymentGroup': 'OTHER',
            'paymentCard': payment_card,
            'buyer': buyer,
            'shippingAddress': address,
            'billingAddress': address,
            'basketItems': basket_items
        }

    
    payment = iyzipay.Payment().create(request1, options)
    payment_json=json.loads(payment.read())
    if payment_json["status"]=="success":
        if indirim != "yok":
            pnr_obj[0].is_used=True
            pnr_obj[0].save()
        BalanceHistory.objects.create(
            user=request.user,
            balance=price,
            adding_balance=True
        )
        request.user.balance += price
        request.user.save()
        products_list=[]
        if price>=750:
            gift=200
            BalanceHistory.objects.create(
                user=request.user,
                balance=gift,
                adding_balance=True,
                is_gift=True
            )
            request.user.balance += gift
            request.user.save()
            products={
                "stock_code":"750 TL + 200 TL OYUN BEDELİ",
                "barcode":"750750200",
                "count":1,
                "price":750
            }
            products_list.append(products)
            if price-750>0:
                products={
                    "stock_code":"1TL",
                    "barcode":"10010",
                    "count":price-750,
                    "price":1
                }
                products_list.append(products)
        elif price>=500 and price<750:
            gift=125
            BalanceHistory.objects.create(
                user=request.user,
                balance=gift,
                adding_balance=True,
                is_gift=True
            )
            request.user.balance += gift
            request.user.save()
            products={
                "stock_code":"500 TL + 125 TL OYUN BEDELİ",
                "barcode":"500500500125",
                "count":1,
                "price":500
            }
            products_list.append(products)
            if price-500>0:
                products={
                    "stock_code":"1TL",
                    "barcode":"10010",
                    "count":price-500,
                    "price":1
                }
                products_list.append(products)
        elif price>=250 and price<500:
            gift=50
            BalanceHistory.objects.create(
                user=request.user,
                balance=gift,
                adding_balance=True,
                is_gift=True
            )
            request.user.balance += gift
            request.user.save()
            products={
                "stock_code":"250 TL + 50 TL OYUN BEDELİ",
                "barcode":"25025025050",
                "count":1,
                "price":250
            }
            products_list.append(products)
            if price-250>0:
                products={
                    "stock_code":"1TL",
                    "barcode":"10010",
                    "count":price-250,
                    "price":1
                }
                products_list.append(products)
        else:
            products={
                "stock_code":"1TL",
                "barcode":"10010",
                "count":price,
                "price":1
            }
            products_list.append(products)
        transaction_id=generate_sha256_for_transactionId(request.user.phone,datetime.now())
        totp = pyotp.TOTP("JKFLSNVITJDNGVXS",digest=hashlib.sha1,interval=3600)
        now=datetime.now()
        url="http://verasql.playland.com.tr:20000/referrer.integration"
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Password":"JKFLSNVITJDNGVXS",
            "OTP":str(totp.now())
        }
        data={
            "Test":False,
            "InvoiceDate":str(now),
            "Host":"mobile.playland.com",
            "BranchCode":"PLAYLAND.MOBIL",
            "TerminalCode":"PLAYLAND142",
            "Type":"Sale",
            "Guid":transaction_id,
            "Current":{
                "phone":request.user.phone,
                "firstname":request.user.firstname,
                "lastname":request.user.lastname,
                "email":request.user.email,
                "title":request.user.firstname+" "+request.user.lastname,
                "address":"TANIMSIZ",
                "tax_office":"SAHIS",
                "city":"ISTANBUL",
                "tax_number":"11111111111",
                "national_id":request.user.member_id
            },
            "Data":products_list
        }
        response = requests.post(url, headers=headers, json=data)
        response=response.json()
        if response["STATE"]:
            Bills.objects.create(
                user=request.user,
                firstname=request.user.firstname,
                lastname=request.user.lastname,
                phone=request.user.phone,
                email=request.user.email,
                title=request.user.firstname+" "+request.user.lastname,
                national_id=request.user.member_id,
                guid=transaction_id,
                invoice_date=now,
                totp=totp.now(),
                product_list=json.dumps(products_list, ensure_ascii=False),
                invoince=response["INVOICE_GUID"],
                is_approve=True,
                price=price
            )
        else:
            Bills.objects.create(
                user=request.user,
                firstname=request.user.firstname,
                lastname=request.user.lastname,
                phone=request.user.phone,
                email=request.user.email,
                title=request.user.firstname+" "+request.user.lastname,
                national_id=request.user.member_id,
                guid=transaction_id,
                invoice_date=now,
                totp=totp.now(),
                product_list=json.dumps(products_list, ensure_ascii=False),
                invoince=response["DESCRIPTION"],
                price=price
            )
        return response_200("success",payment_json)
    else:
        return response_400(payment_json["status"])
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_email_valid(request):
    if request.user.email=="" or request.user.email==None:
        return response_400("email girilmemiş")
    return response_200("success",str(request.user.email))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_or_edit_email(request):
    email=request.data.get("email")
    request.user.email=email
    request.user.save()
    return response_200("success",None)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_branchs(request):
    try:
        branchs_obj = Branchs.objects.all().order_by("-id")
    except ObjectDoesNotExist as e:
        return response_400("filtering is not valid")
    branchs_list = []
    for i in branchs_obj:
        return_obj = {
            "id": i.id,
            "name": i.name,
            "country": i.country,
            "city": i.city,
            "location":i.location,
        }
        branchs_list.append(return_obj)
    branchs_list=sorted(branchs_list, key=lambda x: x['name'])
    return_obj={
        "branch_list":branchs_list
    }
    return response_200("success", return_obj)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delete_person(request):
    request.user.delete()
    return response_200("success",None)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def denemeBillsDelete(request):
    bills_obj=Bills.objects.filter(is_approve=False)
    for i in bills_obj:
        totp = pyotp.TOTP("JKFLSNVITJDNGVXS", digest=hashlib.sha1, interval=3600)


        url = "http://verasql.playland.com.tr:20000/referrer.integration"
            
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Password": "JKFLSNVITJDNGVXS",
            "OTP": str(totp.now())
        }
        data={
            "Test":False,
            "InvoiceDate":str(i.created_at),
            "Host":"mobile.playland.com",
            "BranchCode":"PLAYLAND.MOBIL",
            "TerminalCode":"PLAYLAND142",
            "Type":"Sale",
            "Guid":i.guid,
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
                "Data":json.loads(i.product_list)
            }
        response = requests.post(url, headers=headers, json=data)
        response=response.json()
        if response["STATE"]:
            i.is_approve=True
            i.save()
            i.invoince=response["INVOICE_GUID"]
            i.save()
        else:
            products_list=[]
            price=i.price
            if price>=750:
                gift=200
                products={
                    "stock_code":"750 TL + 200 TL OYUN BEDELİ",
                    "barcode":"750750200",
                    "count":1,
                    "price":750
                }
                products_list.append(products)
                if price-750>0:
                    products={
                        "stock_code":"1TL",
                        "barcode":"10010",
                        "count":price-750,
                        "price":1
                    }
                    products_list.append(products)
            elif price>=500 and price<740:
                gift=125
                products={
                    "stock_code":"500 TL + 250 TL OYUN BEDELİ",
                    "barcode":"500250",
                    "count":1,
                    "price":500
                }
                products_list.append(products)
                if price-500>0:
                    products={
                        "stock_code":"1TL",
                        "barcode":"10010",
                        "count":price-500,
                        "price":1
                    }
                    products_list.append(products)
            elif price>=250 and price<500:
                gift=50
                products={
                    "stock_code":"250 TL + 50 TL OYUN BEDELİ",
                    "barcode":"25025025050",
                    "count":1,
                    "price":250
                }
                products_list.append(products)
                if price-250>0:
                    products={
                        "stock_code":"1TL",
                        "barcode":"10010",
                        "count":price-250,
                        "price":1
                    }
                    products_list.append(products)
            else:
                products={
                    "stock_code":"1TL",
                    "barcode":"10010",
                    "count":price,
                    "price":1
                }
                products_list.append(products)
            url = "http://verasql.playland.com.tr:20000/referrer.integration"
            
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Password": "JKFLSNVITJDNGVXS",
                "OTP": str(totp.now())
            }
            data={
                "Test":False,
                "InvoiceDate":str(i.created_at),
                "Host":"mobile.playland.com",
                "BranchCode":"PLAYLAND.MOBIL",
                "TerminalCode":"PLAYLAND142",
                "Type":"Sale",
                "Guid":i.guid,
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
                i.is_approve=True
                i.save()
                i.invoince=response["INVOICE_GUID"]
                i.save()
            else:
                return response_200("success",response)
    return response_200("success",None)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def denemeBills(request):
    balance_obj=BalanceHistory.objects.filter(adding_balance=True,is_gift=False)
    for i in balance_obj:
        if i.created_at.year==2022 and i.created_at.month<=7 and i.created_at.day<=31:
            products_list=[]
            bills_obj=Bills.objects.filter(invoice_date=i.created_at)
            if len(bills_obj)==0:
                if i.balance>=600:
                    products={
                        "stock_code":"600 TL + 250 TL OYUN BEDELI",
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
                        "stock_code":"400 TL + 150 TL OYUN BEDELI",
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
                        "stock_code":"300 TL + 80 TL OYUN BEDELI",
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
                        "stock_code":"200 TL + 40 TL OYUN BEDELI",
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
                totp = pyotp.TOTP("JKFLSNVITJDNGVXS", digest=hashlib.sha1, interval=3600)


                url = "http://verasql.playland.com.tr:20000/referrer.integration"
            
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Password": "JKFLSNVITJDNGVXS",
                    "OTP": str(totp.now())
                }
                data={
                    "Test":False,
                    "InvoiceDate":str(i.created_at),
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
    return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def jeton_converison(request):
    amount=request.data.get("amount")
    try:
        jeton_obj = jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        jeton_obj = jeton.objects.create(
            user=request.user
        )
    try:
        amount_obj = min_withdrawal_amount.objects.get(id=1)
    except ObjectDoesNotExist as e:
        return response_400('conversion is not exist')
    if amount<amount_obj.min_amount:
        return response_400('Minimum amount is not enough')
    if float(amount) > float(jeton_obj.balance):
        return response_400('You dont have enough jeton')
    request.user.balance += float(amount) / float(amount_obj.tl_to_jeton)
    request.user.save()
    jeton_obj.total += amount
    jeton_obj.save()
    jeton_obj.balance -= amount
    jeton_obj.save()
    jetonHistory.objects.create(
        user=request.user,
        balance=amount,
        adding_balance=False,
        city=None,
        branch=None,
        game_name=None
    )
    BalanceHistory.objects.create(
        user=request.user,
        balance=float(amount) / float(amount_obj.tl_to_jeton),
        adding_balance=True,
        is_gift=True
    )
    return response_200("success", None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_or_create_jeton(request):
    try:
        jeton_obj = jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        jeton_obj = jeton.objects.create(
            user=request.user
        )
    try:
        amount_obj = min_withdrawal_amount.objects.get(id=1)
    except ObjectDoesNotExist as e:
        return response_400('conversion is not exist')
    return_obj = {
        "jeton_amount": jeton_obj.balance,
        "conversional_jeton": jeton_obj.total,
        "tl_to_jeton": amount_obj.tl_to_jeton
    }
    return response_200("success", return_obj)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_jeton_history_for_earnings(request):
    history_obj = jetonHistory.objects.filter(
        user=request.user,adding_balance=True).order_by('-id')
    history_list = []
    
    for i in history_obj:
        return_obj = {
            "user": i.user.firstname+" "+i.user.lastname,
            "history": i.balance,
            "adding_balance": i.adding_balance,
            "city": i.city,
            "branch": i.branch,
            "game_name": i.game_name,
            "created_at": i.created_at,
            "update_at": i.update_at
        }
        history_list.append(return_obj)
    return response_200("success", history_list)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_jeton_history_for_conversions(request):
    history_obj = jetonHistory.objects.filter(
        user=request.user,adding_balance=False).order_by('-id')
    history_list = []
    
    for i in history_obj:
        return_obj = {
            "user": i.user.firstname+" "+i.user.lastname,
            "history": i.balance,
            "adding_balance": i.adding_balance,
            "city": i.city,
            "branch": i.branch,
            "game_name": i.game_name,
            "created_at": i.created_at,
            "update_at": i.update_at
        }
        history_list.append(return_obj)
    return response_200("success", history_list)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_qr_code(request):
    return response_200("success",{"qr_code":request.user.member_id})
    
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pnr_check(request):
    secret_key="JKFLSNVITJDNGVXS"
    totp = pyotp.TOTP(secret_key, digest=hashlib.sha1, interval=3600)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Otp": str(totp.now())
    }
    url = "http://verasql.playland.com.tr:20000/pnr.integration.check"
    PNR=request.data.get("PNR")
    for_add_money=request.data.get("for_add_money")
    data={
        "PNR":str(PNR)
    }
    response = requests.post(url, headers=headers, json=data)
    response=response.json()
    if response["STATE"]!=True:
        return response_400(response["DESCRIPTION"])
    if for_add_money:
        if response["REDUCTION_TYPE"] == "ORAN":
            return response_400("Girdiğiniz PNR yanlış")
    else:
        if response["REDUCTION_TYPE"] == "TUTAR":
            return response_400("Girdiğiniz PNR yanlış")
    return response_200("success", response)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pnr_add_money(request):
    secret_key="JKFLSNVITJDNGVXS"
    totp = pyotp.TOTP(secret_key, digest=hashlib.sha1, interval=3600)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Otp": str(totp.now())
    }
    url = "http://verasql.playland.com.tr:20000/pnr.integration.check"
    PNR=request.data.get("PNR")
    data={
        "PNR":str(PNR)
    }
    response = requests.post(url, headers=headers, json=data)
    response=response.json()
    if response["STATE"]!=True:
        return response_400(response["DESCRIPTION"])
    for_add_money=request.data.get("for_add_money")
    if for_add_money:
        if response["REDUCTION_TYPE"] == "ORAN":
            return response_400("Girdiğiniz PNR yanlış")
    else:
        if response["REDUCTION_TYPE"] == "TUTAR":
            return response_400("Girdiğiniz PNR yanlış")
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Otp": str(totp.now())
    }
    url = "http://verasql.playland.com.tr:20000/pnr.integration.redeem"
    transaction_id=generate_sha256_for_transactionId(request.user.phone,datetime.now())
    data={
        "PNR":str(PNR),
        "TRANSACTION_GUID":transaction_id
    }
    response2 = requests.post(url, headers=headers, json=data)
    response2=response2.json()
    if response2["STATE"]!=True:
        return response_400(response["DESCRIPTION"])
    if response["REDUCTION_TYPE"]=="ORAN":
        PNRTransactions.objects.create(
            user=request.user,
            balance=response["AMOUNT"],
            transaction_guid=transaction_id,
            otp=str(totp.now()),
            transaction_type=response["REDUCTION_TYPE"],
            is_used=False
        )
    else:
        PNRTransactions.objects.create(
            user=request.user,
            balance=response["AMOUNT"],
            transaction_guid=transaction_id,
            otp=str(totp.now()),
            transaction_type=response["REDUCTION_TYPE"],
            is_used=True
        )
        request.user.balance+=response["AMOUNT"]
        request.user.save()
        BalanceHistory.objects.create(
            user=request.user,
            balance=response["AMOUNT"],
            adding_balance=True,
            is_gift=True,
            is_pnr=True
        )
    return response_200("succcess",response2)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def game_info_with_pnr(request,code,pnr_code):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    transaction_id=generate_sha256_for_transactionId(request.user.phone,datetime.now())
    my_obj={
        "machineCode":str(code),
        "memberId":str(request.user.member_id),
        "transactionId":str(transaction_id)
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    x = requests.post("https://api.playland.sade.io/Device/GetPrice", headers=headers, data = json.dumps(my_obj))
    response_obj=x.json()
    if response_obj["status"]==False:
        return response_400("the machine has an error")
    for_child=False
    is_money_enough=True
    if response_obj["machineType"]=="SOFT PLAY2":
        for_child=True
    if request.user.balance<response_obj["price"]:
        is_money_enough=False
    if response_obj["price"]==0:
        return response_400("this machine for personels")
    secret_key="JKFLSNVITJDNGVXS"
    totp = pyotp.TOTP(secret_key, digest=hashlib.sha1, interval=3600)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Otp": str(totp.now())
    }
    url = "http://verasql.playland.com.tr:20000/pnr.integration.check"
    data={
        "PNR":str(pnr_code)
    }
    response = requests.post(url, headers=headers, json=data)
    response=response.json()
    if response["STATE"]!=True:
        return response_400("Girdiğiniz PNR geçerli değildir.")
    if response["REDUCTION_TYPE"]!="ORAN":
        return response_400("Girdiğiniz PNR indirim kodu değildir.")
    return_obj={
        "machine_type":response_obj["machineType"],
        "machine_name":response_obj["machineName"],
        "price":response_obj["price"],
        "new_price":response_obj["price"]-((response_obj["price"]*response["AMOUNT"])/100.0),
        "for_child":for_child,
        "is_money_enough":is_money_enough,
        "your_price":request.user.balance,
        "machine_store": response_obj["machineStore"]
    }
    return response_200("success",return_obj)
    
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def play_game_with_pnr(request,code,pnr_code):
    if not is_verified(request.user.phone):
        return response_400("the user is not verified")
    try:
        jeton_obj = jeton.objects.get(user=request.user)
    except ObjectDoesNotExist as e:
        jeton_obj = jeton.objects.create(
            user=request.user
        )
    try:
        min_amount_obj = min_withdrawal_amount.objects.get(id=1)
    except:
        return response_400("there is no such id")
    transaction_id=generate_sha256_for_transactionId(request.user.phone,datetime.now())
    my_obj={
        "machineCode":str(code),
        "memberId":str(request.user.member_id),
        "transactionId":str(transaction_id)
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    x = requests.post("https://api.playland.sade.io/Device/GetPrice", headers=headers, data = json.dumps(my_obj))
    response_obj=x.json()
    if response_obj["status"]==False:
        return response_400("the machine has an error")
    if response_obj["price"]==0:
        return response_400("this machine for personels")
    if response_obj["machineType"]=="SOFT PLAY2":
        if "family_id" not in request.data:
            return response_400("bad request")
        try:
            Family.objects.get(parent=request.user,is_parent=True)
        except ObjectDoesNotExist as e:
            return response_400("you are not a parent")
        family_id=request.data.get("family_id")
        try:
            family_child=Family.objects.get(parent=request.user,id=family_id)
        except ObjectDoesNotExist as e:
            return response_400("there is no such family")
        this_time_year=(datetime.now()).year
        if this_time_year-(family_child.birthday).year>12:
            return response_400("the child's age is greater than 12")
        if request.user.balance<response_obj["price"]:
            return response_400("the balance is not enough")
        ticket=request.data.get("ticket")
        if "30 dk" in str(response_obj["machineName"]):
            adding_time=1800
        elif "45 dk" in str(response_obj["machineName"]):
            adding_time=2700
        elif "60 dk" in str(response_obj["machineName"]):
            adding_time=3600
        elif "90 dk" in str(response_obj["machineName"]):
            adding_time=5400
        else:
            return response_400("unsupported ticket")
        started_at_ts=datetime.timestamp(datetime.now())
        ended_at_ts=started_at_ts+adding_time
        member_balance=request.user.balance
        
        secret_key="JKFLSNVITJDNGVXS"
        totp = pyotp.TOTP(secret_key, digest=hashlib.sha1, interval=3600)
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Otp": str(totp.now())
        }
        url = "http://verasql.playland.com.tr:20000/pnr.integration.check"
        data={
            "PNR":str(pnr_code)
        }
        response_2 = requests.post(url, headers=headers, json=data)
        response_2=response_2.json()
        if response_2["STATE"]!=True:
            return response_400(response["DESCRIPTION"])
        if response_2["REDUCTION_TYPE"]!="ORAN":
            return response_400("Invalid OTP")
        if member_balance>=500:
            member_balance=499.0
        my_obj={
            "machineCode":str(code),
            "memberId":str(request.user.member_id),
            "transactionId":str(transaction_id),
            "memberBalance":member_balance
        }
        headers = {"Content-Type": "application/json; charset=utf-8"}
        x = requests.post("https://api.playland.sade.io/Device/StartGame", headers=headers, data = json.dumps(my_obj))
        response_obj2=x.json()
        if response_obj2["status"]==True:
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Otp": str(totp.now())
            }
            url = "http://verasql.playland.com.tr:20000/pnr.integration.redeem"
            transaction_id=generate_sha256_for_transactionId(request.user.phone,datetime.now())
            data={
                "PNR":str(pnr_code),
                "TRANSACTION_GUID":transaction_id
            }
            response2 = requests.post(url, headers=headers, json=data)
            response2=response2.json()
            if response2["STATE"]==False:
                return response_400(response2["DESCRIPTION"])
            BalanceHistory.objects.create(
                user=request.user,
                balance=(response_obj["price"]*int(ticket))-((response_obj["price"]*response["AMOUNT"])/100.0),
                adding_balance=False,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            request.user.balance-=(response_obj["price"]*int(ticket))-(((response_obj["price"]*int(ticket))*response["AMOUNT"])/100.0)
            request.user.save()
            Game.objects.create(
                user=request.user,
                gamer=family_child,
                price=response_obj["price"]*int(ticket),
                started_at=datetime.fromtimestamp(started_at_ts),
                ended_at=datetime.fromtimestamp(ended_at_ts),
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
            )
            ChildsOfGames.objects.create(
                parent_name=request.user.firstname,
                parent_surname=request.user.lastname,
                phone=request.user.phone,
                child_name=family_child.firstname,
                child_surname=family_child.lastname,
                is_male=family_child.is_male,
                birthday=family_child.birthday,
                price=response_obj["price"]*int(ticket),
                started_at=datetime.fromtimestamp(started_at_ts),
                ended_at=datetime.fromtimestamp(ended_at_ts),
                is_sent_email=False,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                profile_image=family_child.profile_image
            )
            jeton_obj.balance += (float(response_obj["price"])*float(min_amount_obj.percentage))/float(100)
            jeton_obj.save()
            jetonHistory.objects.create(
                user=request.user,
                balance=(float(response_obj["price"])*float(min_amount_obj.percentage))/float(100),
                adding_balance=True,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            return response_200("success",response_obj2)
        else:
            return response_400("the game not available")
    else:
        try:
            family_parent=Family.objects.get(parent=request.user,is_parent=True)
        except ObjectDoesNotExist as e:
            return response_400("you are not a parent")
        if request.user.balance<response_obj["price"]:
            return response_400("the balance is not enough")
        started_at_ts=datetime.timestamp(datetime.now())
        member_balance=request.user.balance
        if member_balance>=500:
            member_balance=499.0
        my_obj={
            "machineCode":str(code),
            "memberId":str(request.user.member_id),
            "transactionId":str(transaction_id),
            "memberBalance":member_balance
        }
        headers = {"Content-Type": "application/json; charset=utf-8"}
        x = requests.post("https://api.playland.sade.io/Device/StartGame", headers=headers, data = json.dumps(my_obj))
        response_obj3=x.json()
        if str(response_obj3["status"])=="True":
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Otp": str(totp.now())
            }
            url = "http://verasql.playland.com.tr:20000/pnr.integration.redeem"
            transaction_id=generate_sha256_for_transactionId(request.user.phone,datetime.now())
            data={
                "PNR":str(pnr_code),
                "TRANSACTION_GUID":transaction_id
            }
            response2 = requests.post(url, headers=headers, json=data)
            response2=response2.json()
            if response2["STATE"]==False:
                return response_400(response2["DESCRIPTION"])
            BalanceHistory.objects.create(
                user=request.user,
                balance=response_obj["price"]-((response_obj["price"]*response["AMOUNT"])/100.0),
                adding_balance=False,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            request.user.balance-=response_obj["price"]-((response_obj["price"]*response["AMOUNT"])/100.0)
            request.user.save()
            Game.objects.create(
                user=request.user,
                gamer=family_parent,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(started_at_ts),
                ended_at=None,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                is_finished=True
            )
            ChildsOfGames.objects.create(
                parent_name=request.user.firstname,
                parent_surname=request.user.lastname,
                phone=request.user.phone,
                child_name=family_parent.firstname,
                child_surname=family_parent.lastname,
                is_male=family_parent.is_male,
                birthday=family_parent.birthday,
                price=response_obj["price"],
                started_at=datetime.fromtimestamp(started_at_ts),
                ended_at=None,
                is_sent_email=False,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"],
                is_finished=True
            )
            jeton_obj.balance += (float(response_obj["price"])*float(min_amount_obj.percentage))/float(100)
            jeton_obj.save()
            jetonHistory.objects.create(
                user=request.user,
                balance=(float(response_obj["price"])*float(min_amount_obj.percentage))/float(100),
                adding_balance=True,
                city=None,
                branch=response_obj["machineStore"],
                game_name=response_obj["machineName"]
            )
            return response_200("success",response_obj3)
        else:
            return response_400(response_obj3)
            