from datetime import datetime, timedelta, date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from be.responses import response_200, response_400, response_500
from parent.models import BalanceHistory, CustomUser, Family, OTPPhone
from personel.models import ChildsOfGames, Personel, PersonelsOfBranchs
from superuser.models import Branchs, News
from superuser.utils import generate_sha256, in_array

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def super_user_login(request):
    username = request.data.get("username")
    try:
        user_obj = CustomUser.objects.get(username=username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such user")
    if not user_obj.is_admin:
        return response_400("the user is not an superuser")
    password = request.data.get("password")
    if not user_obj.check_password(password):
        return response_400("the password is not true")
    token, _ = Token.objects.get_or_create(user=user_obj)
    return_obj = {
        "token": token.key
    }
    return response_200("success", return_obj)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def super_user_change_password(request):
    old_password=request.data.get("old_password")
    if not request.user.check_password(old_password):
        return response_400("the password is not true")
    password = request.data.get("password")
    password_again = request.data.get("password_again")
    if len(password)<8:
        return response_400("weak password")
    if password != password_again:
        return response_400("the passwords are not match")
    request.user.set_password(password)
    request.user.save()
    return response_200("success",None)
    
    
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_branchs(request,filtering):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    try:
        branchs_obj = Branchs.objects.all().order_by("-id")
    except ObjectDoesNotExist as e:
        return response_400("filtering is not valid")
    branchs_list = []
    for i in branchs_obj:
        if str(filtering) =="all":
            personels_of_branchs_obj = PersonelsOfBranchs.objects.filter(branch=i).order_by("-id")
            return_obj = {
                "id": i.id,
                "name": i.name,
                "country": i.country,
                "city": i.city,
                "location":i.location,
                "personel_count":len(personels_of_branchs_obj)
            }
            branchs_list.append(return_obj)
        else:
            if str(filtering) in str(i.name).lower():
                personels_of_branchs_obj = PersonelsOfBranchs.objects.filter(branch=i).order_by("-id")
                return_obj = {
                    "id": i.id,
                    "name": i.name,
                    "country": i.country,
                    "city": i.city,
                    "location":i.location,
                    "personel_count":len(personels_of_branchs_obj)
                }
                branchs_list.append(return_obj)
    return_obj={
        "branch_list":branchs_list
    }
    return response_200("success", return_obj)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_branchs_count(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branchs_obj = Branchs.objects.all()
    return response_200("success", len(branchs_obj))




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_branch(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branch_id = request.data.get("id")
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such device")
    personels_of_branchs_obj = PersonelsOfBranchs.objects.filter(branch=branch_obj)
    this_time=datetime.now()
    games_count = len(ChildsOfGames.objects.filter(branch=branch_obj.name,started_at__lt=this_time,ended_at__lt=this_time,is_finished=False))
    return_obj = {
        "id": branch_obj.id,
        "name": branch_obj.name,
        "country": branch_obj.country,
        "city": branch_obj.city,
        "location":branch_obj.location,
        "personel_count":len(personels_of_branchs_obj),
        "child_count":games_count
    }
    return response_200("success", return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_cities_and_branchs(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branchs_obj = Branchs.objects.all()
    branchs_list = []
    for i in branchs_obj:
        if not in_array(i, branchs_list):
            branchs_list.append(i.city)
    return_obj = {
        "branchs_count": len(branchs_obj),
        "cities": branchs_list
    }
    return response_200("success", return_obj)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_branch(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    name = request.data.get("name")
    country = request.data.get("country")
    city = request.data.get("city")
    location=request.data.get("location")
    if location==None:
        branch_obj=Branchs.objects.create(
            name=name,
            country=country,
            city=city,
        )
    else:
        branch_obj=Branchs.objects.create(
            name=name,
            country=country,
            city=city,
            location=location
        )
    return response_200("success", branch_obj.id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_branch(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branch_id = request.data.get("id")
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such branch")
    branch_obj.delete()
    return response_200("success", None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_branch(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branch_id = request.data.get("id")
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such branch")
    name = request.data.get("name")
    country = request.data.get("country")
    city = request.data.get("city")
    location=request.data.get("location")
    branch_obj.name = name
    branch_obj.country = country
    branch_obj.city = city
    branch_obj.location = location
    branch_obj.save()
    return response_200("success", None)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_personels(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personels_obj = Personel.objects.all()
    personels_list = []
    for i in personels_obj:
        try:
            personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=i)
            branch_id=personel_of_branch_obj.branch.id
            branch_name=personel_of_branch_obj.branch.name
        except ObjectDoesNotExist as e:
            branch_id="None"
            branch_name="None"
        return_obj = {
            "id": i.id,
            "branch": branch_name,
            "branch_id": branch_id,
            "firstname": i.firstname,
            "lastname": i.lastname,
            "username": i.username,
            "birthday": i.birthday,
            "is_male": i.is_male,
            "phone": i.phone,
            "started_at": i.started_at
        }
        personels_list.append(return_obj)
    return response_200("success", personels_list)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_personels_for_filtering(request,filtering):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personels_obj = Personel.objects.all()
    personels_list = []
    for i in personels_obj:
        if str(filtering) == "all":
            try:
                personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=i)
                branch_id=personel_of_branch_obj.branch.id
                branch_name=personel_of_branch_obj.branch.name
            except ObjectDoesNotExist as e:
                branch_id="None"
                branch_name="None"
            return_obj = {
                "id": i.id,
                "branch": branch_name,
                "branch_id": branch_id,
                "firstname": i.firstname,
                "lastname": i.lastname,
                "username": i.username,
                "birthday": i.birthday,
                "is_male": i.is_male,
                "phone": i.phone,
                "started_at": i.started_at
            }
            personels_list.append(return_obj)
        elif str(filtering) in (str(i.firstname).lower()+" "+str(i.lastname).lower()):
            try:
                personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=i)
                branch_id=personel_of_branch_obj.branch.id
                branch_name=personel_of_branch_obj.branch.name
            except ObjectDoesNotExist as e:
                branch_id="None"
                branch_name="None"
            return_obj = {
                "id": i.id,
                "branch": branch_name,
                "branch_id": branch_id,
                "firstname": i.firstname,
                "lastname": i.lastname,
                "username": i.username,
                "birthday": i.birthday,
                "is_male": i.is_male,
                "phone": i.phone,
                "started_at": i.started_at
            }
            personels_list.append(return_obj)
    return response_200("success", personels_list)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_personels_count(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personels_obj = Personel.objects.all()
    return response_200("success", len(personels_obj))
    
    
        
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_male_personels_count(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personels_obj = Personel.objects.filter(is_male=True)
    return response_200("success", len(personels_obj))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_female_personels_count(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personels_obj = Personel.objects.filter(is_male=False)
    return response_200("success", len(personels_obj))
    
    
  
  
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def birthday_personel(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    this_time=datetime.strptime(str(date.today()),"%Y-%m-%d")
    personels_obj = Personel.objects.filter(birthday=this_time)
    returning_list=[]
    for i in personels_obj:
        try:
            personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=i)
            branch_id=personel_of_branch_obj.branch.id
            branch_name=personel_of_branch_obj.branch.name
        except ObjectDoesNotExist as e:
            branch_id="None"
            branch_name="None"
        return_obj={
            "id":i.id,
            "branch": branch_name,
            "branch_id": branch_id,
            "firstname":i.firstname,
            "lastname":i.lastname,
            "username":i.username,
            "birthday":i.birthday,
            "is_male":i.is_male,
            "phone":i.phone,
            "started_at":i.started_at,
            "created_at":i.created_at,
            "update_at":i.update_at
        }
        returning_list.append(return_obj)
    return_obj={
        "birthday_personel_count":len(personels_obj),
        "personels":returning_list
    }
    return response_200("success",return_obj)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_branch_personels(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branch_id = request.data.get("id")
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such branch")
    personels_of_branchs_obj = PersonelsOfBranchs.objects.filter(branch=branch_obj)
    personels_list = []
    for i in personels_of_branchs_obj:
        return_obj = {
            "id": i.personel.id,
            "branch": i.branch.name,
            "branch_id": i.branch.id,
            "firstname": i.personel.firstname,
            "lastname": i.personel.lastname,
            "username": i.personel.username,
        }
        personels_list.append(return_obj)
    return response_200("success", personels_list)
    
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_branch_personels_count(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branch_id = request.data.get("id")
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such branch")
    personels_of_branchs_obj = PersonelsOfBranchs.objects.filter(branch=branch_obj)
    return response_200("success",len(personels_of_branchs_obj))
    
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_personel(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personel_id = request.data.get("id")
    try:
        personel_obj = Personel.objects.get(id=personel_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
        branch_id=personel_of_branch_obj.branch.id
        branch_name=personel_of_branch_obj.branch.name
    except ObjectDoesNotExist as e:
        branch_id="None"
        branch_name="None"
    return_obj = {
        "id": personel_obj.id,
        "branch": branch_name,
        "branch_id": branch_id,
        "firstname": personel_obj.firstname,
        "lastname": personel_obj.lastname,
        "username": personel_obj.username,
        "birthday":personel_obj.birthday,
        "is_male":personel_obj.is_male,
        "started_at":personel_obj.started_at,
        "phone":personel_obj.phone
    }
    return response_200("success", return_obj)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_personel(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    username = request.data.get("username")
    try:
        Personel.objects.get(username=username)
        return response_400("the username already taken")
    except ObjectDoesNotExist as e:
        password = request.data.get("password")
        phone = request.data.get("phone")
        personel_birthday=datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
        personel_started_at=datetime.strptime(request.data.get("started_at"), "%Y-%m-%d")
        is_male=request.data.get("is_male")
        if len(password) < 8:
            return response_400("the password must be 8 digit")
        try:
            CustomUser.objects.get(phone=phone)
            return response_400("the phone already taken")
        except ObjectDoesNotExist as e:
            Personel.objects.create(
                firstname=firstname,
                lastname=lastname,
                username=username,
                birthday=personel_birthday,
                started_at=personel_started_at,
                is_male=is_male,
                phone=phone
            )
            user_obj = CustomUser.objects.create(
                firstname=firstname,
                lastname=lastname,
                username=username,
                birthday=personel_birthday,
                is_personel=True,
                phone=phone
            )
            user_obj.set_password(password)
            user_obj.save()
            return response_200("success", None)
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_personel_to_branch(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    branch_id = request.data.get("id")
    try:
        branch_obj = Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such branch")
    personels=request.data.get("usernames")
    for i in personels:
        try:
            personel_ojb=Personel.objects.get(username=i)
        except ObjectDoesNotExist as e:
            return response_400("there is no such personel")
        try:
            PersonelsOfBranchs.objects.get(personel=personel_ojb)
            return response_400("the personel already is in the branch")
        except ObjectDoesNotExist as e:
            PersonelsOfBranchs.objects.create(
                branch=branch_obj,
                personel=personel_ojb
            )
    return response_200("success",None)
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_personel_from_branch(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personel_id=request.data.get("personel_id")
    try:
        personel_ojb=Personel.objects.get(id=personel_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_ojb)
    except ObjectDoesNotExist as e:
        return response_400("the personel is already none branch")
    personel_branch_obj.delete()
    return response_200("success",None)
    
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_personel(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personel_id=request.data.get("personel_id")
    try:
        personel_ojb=Personel.objects.get(id=personel_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    personel_ojb.delete()
    return response_200("success",None)
    
    
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_personel_with_password(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personel_id = request.data.get("id")
    try:
        personel_obj = Personel.objects.get(id=personel_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        user_obj=CustomUser.objects.get(username=personel_obj.username,is_personel=True)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    username = request.data.get("username")
    try:
        personel_obj2=Personel.objects.get(username=username)
        if personel_obj2!=personel_obj:
            return response_400("the username already taken")
        password = request.data.get("password")
        phone = request.data.get("phone")
        personel_birthday=datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
        personel_started_at=datetime.strptime(request.data.get("started_at"), "%Y-%m-%d")
        is_male=request.data.get("is_male")
        if len(password) < 8:
            return response_400("the password must be 8 digit")
        personel_obj.firstname = firstname
        personel_obj.lastname = lastname
        personel_obj.username = username
        personel_obj.phone = phone
        personel_obj.birthday = personel_birthday
        personel_obj.started_at = personel_started_at
        personel_obj.is_male = is_male
        personel_obj.save()
        user_obj.firstname=firstname
        user_obj.lastname=lastname
        user_obj.username=username
        user_obj.phone=phone
        user_obj.birthday=personel_birthday
        user_obj.set_password(password)
        user_obj.save()
        return response_200("success",None)
    except ObjectDoesNotExist as e:
        password = request.data.get("password")
        phone = request.data.get("phone")
        personel_birthday=datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
        personel_started_at=datetime.strptime(request.data.get("started_at"), "%Y-%m-%d")
        is_male=request.data.get("is_male")
        if len(password) < 8:
            return response_400("the password must be 8 digit")
        personel_obj.firstname = firstname
        personel_obj.lastname = lastname
        personel_obj.username = username
        personel_obj.phone = phone
        personel_obj.birthday = personel_birthday
        personel_obj.started_at = personel_started_at
        personel_obj.is_male = is_male
        personel_obj.save()
        user_obj.firstname=firstname
        user_obj.lastname=lastname
        user_obj.username=username
        user_obj.phone=phone
        user_obj.birthday=personel_birthday
        user_obj.set_password(password)
        user_obj.save()
        return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_personel_without_password(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    personel_id = request.data.get("id")
    try:
        personel_obj = Personel.objects.get(id=personel_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    username = request.data.get("username")
    try:
        personel_obj2=Personel.objects.get(username=username)
        if personel_obj2!=personel_obj:
            return response_400("the username already taken")
        phone = request.data.get("phone")
        personel_birthday=datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
        personel_started_at=datetime.strptime(request.data.get("started_at"), "%Y-%m-%d")
        is_male=request.data.get("is_male")
        personel_obj.firstname = firstname
        personel_obj.lastname = lastname
        personel_obj.username = username
        personel_obj.phone = phone
        personel_obj.birthday = personel_birthday
        personel_obj.started_at = personel_started_at
        personel_obj.is_male = is_male
        personel_obj.save()
        return response_200("success",None)
    except ObjectDoesNotExist as e:
        phone = request.data.get("phone")
        personel_birthday=datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
        personel_started_at=datetime.strptime(request.data.get("started_at"), "%Y-%m-%d")
        is_male=request.data.get("is_male")
        personel_obj.firstname = firstname
        personel_obj.lastname = lastname
        personel_obj.username = username
        personel_obj.phone = phone
        personel_obj.birthday = personel_birthday
        personel_obj.started_at = personel_started_at
        personel_obj.is_male = is_male
        personel_obj.save()
        return response_200("success",None)

    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def non_pending_money_and_users_count(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    users=CustomUser.objects.filter(is_admin=False,is_personel=False)
    total_money=0
    for i in users:
        total_money+=i.balance
    return_obj={
        "user_count":len(users),
        "non_pending_money":str(total_money)
    }
    return response_200("success",return_obj)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_news(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    news_obj = News.objects.all().order_by('-id')
    news_list = []
    for news in news_obj:
        return_obj = {
            "id":news.id,
            "title": news.title,
            "short_description": news.short_description,
            "description": news.description,
            "image": "/media/"+str(news.image),
            "created_at":news.created_at,
            "is_campaign":news.is_campaign
        }
        news_list.append(return_obj)
    return response_200("success", news_list)
    
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_news(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    title=request.data.get("title")
    short_description=request.data.get("short_description")
    description=request.data.get("description")
    image=request.data.get("image")
    is_campaign=request.data.get("is_campaign")
    News.objects.create(
        title=title,
        short_description=short_description,
        description=description,
        image=image,
        is_campaign=is_campaign
    )
    return response_200("success",None)
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_news(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    id=request.data.get("id")
    try:
        news_obj=News.objects.get(id=id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such news")
    title=request.data.get("title")
    short_description=request.data.get("short_description")
    description=request.data.get("description")
    image=request.data.get("image")
    is_campaign=request.data.get("is_campaign")
    news_obj.title=title
    news_obj.short_description=short_description
    news_obj.description=description
    news_obj.image=image
    news_obj.is_campaign=is_campaign
    news_obj.save()
    return response_200("success",None)
    
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_news(request):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    id=request.data.get("id")
    try:
        news_obj=News.objects.get(id=id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such news")
    news_obj.delete()
    return response_200("success",None)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_game_history(request,filtering):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    try:
        games=ChildsOfGames.objects.all().order_by("-id")
    except ObjectDoesNotExist as e:
        return response_400("filtering is not valid")
    games_list=[]
    for i in games:
        if str(filtering)=="all":
            return_obj={
                "id":i.id,
                "parent_name":i.parent_name,
                "parent_surname":i.parent_surname,
                "phone":i.phone,
                "child_name":i.child_name,
                "child_surname":i.child_surname,
                "is_male":i.is_male,
                "birthday":i.birthday,
                "price":i.price,
                "started_at":i.started_at,
                "ended_at":i.ended_at,
                "is_sent_email":i.is_sent_email,
                "city":i.city,
                "branch":i.branch,
                "game_name":i.game_name,
                "is_finished":i.is_finished,
                "created_at":i.created_at,
                "update_at":i.update_at,
                "profile_image":"/media/"+str(i.profile_image)
            }
            games_list.append(return_obj)
        else:
            if str(filtering) in str(i.game_name).lower():
                return_obj={
                    "id":i.id,
                    "parent_name":i.parent_name,
                    "parent_surname":i.parent_surname,
                    "phone":i.phone,
                    "child_name":i.child_name,
                    "child_surname":i.child_surname,
                    "is_male":i.is_male,
                    "birthday":i.birthday,
                    "price":i.price,
                    "started_at":i.started_at,
                    "ended_at":i.ended_at,
                    "is_sent_email":i.is_sent_email,
                    "city":i.city,
                    "branch":i.branch,
                    "game_name":i.game_name,
                    "is_finished":i.is_finished,
                    "created_at":i.created_at,
                    "update_at":i.update_at,
                    "profile_image":"/media/"+str(i.profile_image)
                }
                games_list.append(return_obj)
    return_obj={
        "games_history":games_list
    }
    return response_200("success",return_obj)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_history(request,game_id):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    try:
        game_obj=ChildsOfGames.objects.get(id=game_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such history")
    return_obj={
        "id":game_obj.id,
        "parent_name":game_obj.parent_name,
        "parent_surname":game_obj.parent_surname,
        "phone":game_obj.phone,
        "child_name":game_obj.child_name,
        "child_surname":game_obj.child_surname,
        "is_male":game_obj.is_male,
        "birthday":i.birthday,
        "price":game_obj.price,
        "started_at":game_obj.started_at,
        "ended_at":game_obj.ended_at,
        "is_sent_email":game_obj.is_sent_email,
        "city":game_obj.city,
        "branch":game_obj.branch,
        "game_name":game_obj.game_name,
        "is_finished":game_obj.is_finished,
        "created_at":game_obj.created_at,
        "update_at":game_obj.update_at,
        "profile_image":"/media/"+str(game_obj.profile_image)
    }
    return response_200("success",return_obj)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_history_by_branch(request,branch_id,filtering):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    try:
        branch_obj=Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400("There is no such Branch")
    try:
        games=ChildsOfGames.objects.filter(branch=branch_obj.name).order_by("-id")
    except ObjectDoesNotExist as e:
        return response_400("filtering is not valid")
    games_list=[]
    for i in games:
        if filtering=="all":
            return_obj={
                "id":i.id,
                "parent_name":i.parent_name,
                "parent_surname":i.parent_surname,
                "phone":i.phone,
                "child_name":i.child_name,
                "child_surname":i.child_surname,
                "is_male":i.is_male,
                "birthday":i.birthday,
                "price":i.price,
                "started_at":i.started_at,
                "ended_at":i.ended_at,
                "is_sent_email":i.is_sent_email,
                "city":i.city,
                "branch":i.branch,
                "game_name":i.game_name,
                "is_finished":i.is_finished,
                "created_at":i.created_at,
                "update_at":i.update_at,
                "profile_image":"/media/"+str(i.profile_image)
            }
            games_list.append(return_obj)
        else:
            if str(filtering) in str(i.game_name).lower():
                return_obj={
                    "id":i.id,
                    "parent_name":i.parent_name,
                    "parent_surname":i.parent_surname,
                    "phone":i.phone,
                    "child_name":i.child_name,
                    "child_surname":i.child_surname,
                    "is_male":i.is_male,
                    "birthday":i.birthday,
                    "price":i.price,
                    "started_at":i.started_at,
                    "ended_at":i.ended_at,
                    "is_sent_email":i.is_sent_email,
                    "city":i.city,
                    "branch":i.branch,
                    "game_name":i.game_name,
                    "is_finished":i.is_finished,
                    "created_at":i.created_at,
                    "update_at":i.update_at,
                    "profile_image":"/media/"+str(i.profile_image)
                }
                games_list.append(return_obj)
    return_obj={
        "games_history":games_list
    }
    return response_200("success",return_obj)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_in_game_history_by_branch(request,branch_id,filtering):
    if not request.user.is_admin:
        return response_400("the user is not an superuser")
    try:
        branch_obj=Branchs.objects.get(id=branch_id)
    except ObjectDoesNotExist as e:
        return response_400("There is no such Branch")
    this_time=datetime.now();
    try:
        games=ChildsOfGames.objects.filter(branch=branch_obj.name,started_at__lt=this_time,ended_at__lt=this_time,is_finished=False).order_by("-id")
    except ObjectDoesNotExist as e:
        return response_400("filtering is not valid")
    games_list=[]
    for i in games:
        if filtering=="all":
            return_obj={
                "id":i.id,
                "parent_name":i.parent_name,
                "parent_surname":i.parent_surname,
                "phone":i.phone,
                "child_name":i.child_name,
                "child_surname":i.child_surname,
                "is_male":i.is_male,
                "birthday":i.birthday,
                "price":i.price,
                "started_at":i.started_at,
                "ended_at":i.ended_at,
                "is_sent_email":i.is_sent_email,
                "city":i.city,
                "branch":i.branch,
                "game_name":i.game_name,
                "is_finished":i.is_finished,
                "created_at":i.created_at,
                "update_at":i.update_at,
                "profile_image":"/media/"+str(i.profile_image)
            }
            games_list.append(return_obj)
        else:
            if str(filtering) in str(i.game_name).lower():
                return_obj={
                    "id":i.id,
                    "parent_name":i.parent_name,
                    "parent_surname":i.parent_surname,
                    "phone":i.phone,
                    "child_name":i.child_name,
                    "child_surname":i.child_surname,
                    "is_male":i.is_male,
                    "birthday":i.birthday,
                    "price":i.price,
                    "started_at":i.started_at,
                    "ended_at":i.ended_at,
                    "is_sent_email":i.is_sent_email,
                    "city":i.city,
                    "branch":i.branch,
                    "game_name":i.game_name,
                    "is_finished":i.is_finished,
                    "created_at":i.created_at,
                    "update_at":i.update_at,
                    "profile_image":"/media/"+str(i.profile_image)
                }
                games_list.append(return_obj)
    return_obj={
        "games_history":games_list
    }
    return response_200("success",return_obj)