from django.urls import path

from superuser.views import add_branch, add_news, add_personel, add_personel_to_branch, all_branchs, all_branchs_count, all_cities_and_branchs, all_female_personels_count, all_game_history, all_male_personels_count, all_news, all_personels, all_personels_count, all_personels_for_filtering, birthday_personel, delete_news, edit_branch, edit_news, edit_personel_with_password, edit_personel_without_password, get_branch, get_branch_personels, get_branch_personels_count, get_game_history, get_game_history_by_branch, get_personel, non_pending_money_and_users_count, remove_branch, super_user_change_password, super_user_login, get_in_game_history_by_branch, delete_personel_from_branch, delete_personel


urlpatterns = [
    path("superuser-login",super_user_login),
    path("superuser-change-password",super_user_change_password),
    path("all-branchs/<str:filtering>",all_branchs),
    path("all-branchs-count",all_branchs_count),
    path("get-branch",get_branch),
    path("all-cities-and-branchs",all_cities_and_branchs),
    path("add-branch",add_branch),
    path("remove-branch",remove_branch),
    path("edit-branch",edit_branch),
    path("all-personels",all_personels),
    path("all-personels-with-filtering/<str:filtering>",all_personels_for_filtering),
    path("all-personels-count",all_personels_count),
    path("all-male-personels-count",all_male_personels_count),
    path("all-female-personels-count",all_female_personels_count),
    path("birthday-personel",birthday_personel),
    path("get-branch-personels",get_branch_personels),
    path("get-branch-personels-count",get_branch_personels_count),
    path("get-personel",get_personel),
    path("add-personel",add_personel),
    path("add-personel-to-branch",add_personel_to_branch),
    path("edit-personel-with-password",edit_personel_with_password),
    path("edit-personel-without-password",edit_personel_without_password),
    path("non-pending-money-and-users-count",non_pending_money_and_users_count),
    path("all-news",all_news),
    path("add-news",add_news),
    path("edit-news",edit_news),
    path("delete-news",delete_news),
    path("all-game-history/<str:filtering>",all_game_history),
    path("get-game-history/<int:game_id>",get_game_history),
    path("get-game-history-by-branch/<str:branch_id>/<str:filtering>",get_game_history_by_branch),
    path("get-in-game-history-by-branch/<str:branch_id>/<str:filtering>",get_in_game_history_by_branch),
    path("delete-personel-from-branch",delete_personel_from_branch),
    path("delete-personel",delete_personel)
]