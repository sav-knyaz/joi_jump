from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    #path('<int:pk>', views.PageLesson.as_view(), name='page-lesson'),
    path('about', views.about, name='about'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('numPhone', views.req_phone, name='formPhone'),
    path('next', views.next, name='next'),
    path('newpass', views.change_password, name='newpass'),
    path('registration', views.regist, name='regist'),
    path('timetable', views.time_table, name='timetable'),
    path('personArea', views.person_area, name='person'),
    path('error', views.error_page, name='error'),
]