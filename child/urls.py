from django.urls import path
from .views import index, login, register, quit_, token_password, psw_token, personal, activiteroom, introduction, verification, community, addchild, \
    modifychild, forget, forget_token, \
    add_dependent, modify_dependent, join_activite, feedback

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('quit/', quit_, name='quit'),
    path('token_password', token_password, name='token_password'),
    path('psw_token', psw_token, name='psw_token'),
    path('personal/', personal, name='personal'),
    path('forget/', forget, name='forget'),
    path('forget_token/', forget_token, name='forget_token'),
    path('activiteroom', activiteroom, name='activiteroom'),
    path('verification/', verification, name='verification'),
    path('introduction/', introduction, name='introduction'),
    path('community/', community, name='community'),
    path('addchild/', addchild, name='addchild'),
    path('modifychild/', modifychild, name='modifychild'),
    path('add_dependent/', add_dependent, name='add_dependent'),
    path('modify_dependent/', modify_dependent, name='modify_dependent'),
    path('join_activite/', join_activite, name='join_activite'),
    path('feedback/', feedback, name='feedback'),
]
