from django.urls import path

from personel.views import get_branch_detail, get_branch_personels, get_branch_personels_count, get_childs_in_game, get_childs_in_game_count, give_child_to_parent, give_child_to_parent_verification, login, send_sms_to_parent, get_game_history, add_child_games, toy_list


urlpatterns = [
    path("personel-login",login),
    path("get-branch-detail",get_branch_detail),
    path("get-branch-personels-count",get_branch_personels_count),
    path("get-branch-personels",get_branch_personels),
    path("get-childs-in-game",get_childs_in_game),
    path("get-childs-in-game-count",get_childs_in_game_count),
    path("give-child-to-parent",give_child_to_parent),
    path("give-child-to-parent-verification",give_child_to_parent_verification),
    path("send-sms-to-parent",send_sms_to_parent),
    path("get-game-history/<str:filtering>",get_game_history),
    path("add-child-game",add_child_games),
    path("toy-list",toy_list)


]