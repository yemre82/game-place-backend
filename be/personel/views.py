from datetime import datetime, date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from personel.models import ChildsOfGames, Games
from be.responses import response_200, response_400

from parent.models import CustomUser, Family, Game, OTPGetChild
from parent.utils import generate_random_num, sendSMSVerification
from personel.models import Personel, PersonelsOfBranchs, ChildsOfGames
from personel.utils import sendSMSForParents

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username=request.data.get("username")
    try:
        user_obj=CustomUser.objects.get(username=username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    if user_obj.is_personel==False:
        return response_400("the user is not a personel")
    try:
        personel_obj=Personel.objects.get(username=username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    password=request.data.get("password")
    if not user_obj.check_password(password):
        return response_400("the password is not true")
    token, _ = Token.objects.get_or_create(user=user_obj)
    return_obj = {
        "token": token.key
    }
    return response_200("success", return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branch_detail(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    return_obj={
        "id":personel_of_branch_obj.branch.id,
        "country":personel_of_branch_obj.branch.country,
        "city":personel_of_branch_obj.branch.city,
        "name":personel_of_branch_obj.branch.name,
        "location":personel_of_branch_obj.branch.location
    }
    return response_200("success",return_obj)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branch_personels_count(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    personel_of_branch_obj=PersonelsOfBranchs.objects.filter(branch=personel_of_branch_obj.branch)
    return response_200("success",str(len(personel_of_branch_obj)))



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branch_personels(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    returning_list=[]
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    personel_of_branch_obj=PersonelsOfBranchs.objects.filter(branch=personel_of_branch_obj.branch)
    for i in personel_of_branch_obj:
        return_obj = {
            "id": i.personel.id,
            "branch": i.branch.name,
            "branch_id": i.branch.id,
            "firstname": i.personel.firstname,
            "lastname": i.personel.lastname,
            "username": i.personel.username,
            "birthday":i.personel.birthday,
            "is_male":i.personel.is_male,
            "started_at":i.personel.started_at,
            "phone":i.personel.phone
        }
        returning_list.append(return_obj)
    return response_200("success",returning_list)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_childs_in_game(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    this_time=datetime.now()
    game_obj=ChildsOfGames.objects.filter(is_finished=False,branch=personel_of_branch_obj.branch.name).order_by("-id")
    returning_list=[]
    for i in game_obj:
        remaining_time_ts=datetime.timestamp(i.ended_at)-datetime.timestamp(this_time)
        how_much_ticket_played=(datetime.timestamp(i.ended_at)-datetime.timestamp(i.started_at))/1800
        one_ticket_price=(i.price)/how_much_ticket_played
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
            "remaining_time":remaining_time_ts,
            "is_sent_email":i.is_sent_email,
            "city":i.city,
            "branch":i.branch,
            "game_name":i.game_name,
            "is_finished":i.is_finished,
            "created_at":i.created_at,
            "update_at":i.update_at,
            "profile_image":"/media/"+str(i.profile_image)
        }
        returning_list.append(return_obj)
    return response_200("success",returning_list)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_childs_in_game_count(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    this_time=datetime.now()
    game_obj=ChildsOfGames.objects.filter(is_finished=False,branch=personel_of_branch_obj.branch.name).order_by("-id")
    return response_200("success",len(game_obj))



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def give_child_to_parent(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    this_time=datetime.now()
    game_obj=ChildsOfGames.objects.filter(is_finished=False,branch=personel_of_branch_obj.branch.name).order_by("-id")
    if len(game_obj)==0:
        return response_400("the branch has no child in game")
    game_id=request.data.get("game_id")
    try:
        game_obj=ChildsOfGames.objects.get(is_finished=False,id=game_id,branch=personel_of_branch_obj.branch.name)
    except ObjectDoesNotExist as e:
        return response_400("there is no such game")
    otp = generate_random_num()
    description="get-child"
    try:
        game2_obj=Game.objects.get(started_at=game_obj.started_at,ended_at=game_obj.ended_at,is_finished=False,branch=personel_of_branch_obj.branch.name)
        OTPGetChild.objects.create(
            user=game2_obj.user,
            phone=game_obj.phone,
            otp=otp,
            description=description,
        )
    except ObjectDoesNotExist as e:
        OTPGetChild.objects.create(
            user=request.user,
            phone=game_obj.phone,
            otp=otp,
            description=description,
        )
    sendSMSVerification(otp,[game_obj.phone])
    return response_200("success",None)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def give_child_to_parent_verification(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    game_obj=ChildsOfGames.objects.filter(is_finished=False,branch=personel_of_branch_obj.branch.name).order_by("-id")
    if len(game_obj)==0:
        return response_400("the branch has no child in game")
    game_id=request.data.get("game_id")
    try:
        game_obj=ChildsOfGames.objects.get(is_finished=False,id=game_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such game")
    otp=request.data.get("otp")
    try:
        otp_obj=OTPGetChild.objects.get(otp=otp,is_verified=False)
    except ObjectDoesNotExist as e:
        return response_400("there is no such otp")
    otp_obj.is_verified=True
    otp_obj.save()
    game_obj.is_finished=True
    game_obj.save()
    try:
        game2_obj=Game.objects.get(is_finished=False,started_at=game_obj.started_at,ended_at=game_obj.ended_at,branch=personel_of_branch_obj.branch.name)
        game2_obj.is_finished=True
        game2_obj.save()
        return response_200("success",None)
    except ObjectDoesNotExist as e:
        return response_200("success",None)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_sms_to_parent(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    this_time=datetime.now()
    game_obj=ChildsOfGames.objects.filter(is_finished=False,branch=personel_of_branch_obj.branch.name).order_by("-id")
    if len(game_obj)==0:
        return response_400("the branch has no child in game")
    game_id=request.data.get("game_id")
    try:
        game_obj=ChildsOfGames.objects.get(is_finished=False,id=game_id)
    except ObjectDoesNotExist as e:
        return response_400("there is no such game")
    message=request.data.get("message")
    if len(message)<1:
        return response_400("the message is not valid")
    sendSMSForParents([game_obj.phone],str(message))
    return response_200("success",None)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_history(request,filtering):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    games=ChildsOfGames.objects.filter(branch=personel_of_branch_obj.branch.name).order_by("-id")
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
    
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_child_games(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    name=request.data.get("name")
    surname=request.data.get("surname")
    parent_name=request.data.get("parent_name")
    parent_surname=request.data.get("parent_surname")
    birthday = datetime.strptime(request.data.get("birthday"), "%Y-%m-%d")
    this_time=datetime.now()
    if this_time.year-birthday.year>12:
        return response_400("the child's age must be under 12")
    parent_phone=request.data.get("parent_phone")
    game_name=request.data.get("game_name")
    is_male=request.data.get("is_male")
    price=request.data.get("price")
    ticket=request.data.get("ticket")
    started_at=datetime.now()
    ended_at=datetime.fromtimestamp(datetime.timestamp(started_at)+(1800*ticket))
    ChildsOfGames.objects.create(
        parent_name=parent_name,
        parent_surname=parent_surname,
        phone=parent_phone,
        child_name=name,
        child_surname=surname,
        is_male=is_male,
        birthday=birthday,
        price=price,
        started_at=started_at,
        ended_at=ended_at,
        is_sent_email=False,
        city=personel_of_branch_obj.branch.city,
        branch=personel_of_branch_obj.branch.name,
        game_name=game_name
    )
    return response_200("success",None)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def toy_list(request):
    try:
        personel_obj=Personel.objects.get(username=request.user.username)
    except ObjectDoesNotExist as e:
        return response_400("there is no such personel")
    try:
        personel_of_branch_obj=PersonelsOfBranchs.objects.get(personel=personel_obj)
    except ObjectDoesNotExist as e:
        return response_400("the personel is not in the branch")
    games_objs=Games.objects.filter(branch=personel_of_branch_obj.branch)
    toys_list=[]
    for i in games_objs:
        return_obj={
            "branch":i.branch.name,
            "game_name":i.game_name,
            "machine_type":i.machine_type
        }
        toys_list.append(return_obj)
    return response_200("success",toys_list)