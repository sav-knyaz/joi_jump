from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import LoginForms, Registration, FormPhone, FormXcode
from .models import Lessons, CustomUser, PhoneXcode, TimeTable, Subscription
from .helper import translat_in_russion, send_sms, change_subcr_time_table, delete_old_lesson
import datetime
import random
import json
from django.http import JsonResponse, HttpResponseRedirect


#order_by метод благодаря которому можно сортировать поля

def index(request):
    delete_old_lesson()
    #если пользователь авторизован тогда он добавляет себе занятие в расписание
    if request.user.is_authenticated:

        user = request.user
        time_table = TimeTable.objects.filter(user=user)
        change_subcr_time_table(user, time_table)

        if request.method == 'POST':

            json_string = request.body.decode('utf-8')
            id_lesson = int(json.loads(json_string)['id'])

            lesson = Lessons.objects.get(id=id_lesson)
            #проверка есть ли запись
            tt = TimeTable.objects.filter(lesson=lesson, user=user).count()
            
            if tt == 0:
                TimeTable.objects.create(lesson=lesson, user=user)
                
                return JsonResponse({'messeg': 'Вы записаны на занятие!'})
            else:
                return JsonResponse({'messeg': 'Вы уже записаны на это занятие!'})
            
    lessons = Lessons.objects.all()
    lessons = sorted(lessons,key=lambda x: x.data)[:5]
    for el in lessons:
        el.data = translat_in_russion(el.data.strftime('%d %B'))

    return render(request, 'main/index.html', {'tittle':'Главная страница', 'lessons':lessons,})



def about(request):
    delete_old_lesson()

    return render(request, 'main/about.html')





def login_user(request):
    delete_old_lesson()
    error = ''
    if request.method == 'POST':
        form = LoginForms(request.POST)
        if form.is_valid():

            cd = form.cleaned_data
            user = authenticate( phone=cd['phone'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session['phone'] = cd['phone']
                    return redirect('home')
            else:
                error = 'Неверный номер телефона или пароль'
        else: 
            error = 'Не правильно введен логин или пароль'


    login_form = LoginForms()
    return render(request, 'main/login.html', {'form': login_form, 'error':error})

def logout_user(request):
    logout(request)
    return redirect('home')






def req_phone(request):
    error = ''

    if request.method == 'POST':
        form = FormPhone(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            #проверяем есть ли пользователь с таким телефоном
            # if CustomUser.objects.filter(phone=phone).count() == 0:
            request.session['phone'] = phone
            xcode = str(random.randint(1000, 9999))
            PhoneXcode.objects.filter(phone=phone).delete()
            PhoneXcode.objects.create(phone=phone, xcode=xcode)

            return redirect('next')
            
        else:
            error = 'Не правильно заполнена форма! Введите цифры после +7 или 8'

    form_phone = FormPhone()
    return render(request, 'main/formPhone.html', {'form': form_phone, 'error': error})


def next(request):

    error = ''

    phone = request.session.get('phone', None)
#если тел не сохраился в сессии, то отправляем юзера на страницу formPhone
    if  phone is not None:
        phone_xcode = PhoneXcode.objects.get(phone=phone)
        
        result_send_sms = send_sms(phone, 'Код подтверждения:', phone_xcode.xcode)

        #Если сервис смс-центр не работает, то отправляем на страницу с ошибкой
        print(result_send_sms)
        if result_send_sms == False:
            return render(request, 'main/error.html')
    
    else: 
        return redirect('formPhone')

#проверяем отправленный код
    if request.method == 'POST':
        form = FormXcode(request.POST)
        if form.is_valid():
            phone_xcode = PhoneXcode.objects.filter(phone=phone, xcode=form.cleaned_data['xcode']).count()
            user = CustomUser.objects.filter(phone=phone)
#если пользователь ЕСТЬ в бд и он подтвердил свой номер, то может менять пароль
            if user.count() != 0 and phone_xcode != 0:
                return redirect('newpass')
#если пользователя НЕТ в бд и он подтвердил свой номер, то может создать себе аккаунт
            if phone_xcode != 0:
                return redirect('regist')
            else:
                error = 'Неверный код!'
        else:
            error = 'Неверно заполнена форма!'

    form_xcode = FormXcode()
    return render(request, 'main/next.html', {'form':form_xcode, 'error': error})

    



def regist(request):
    error = ''
    if request.method == 'POST':
        form_reg = Registration(request.POST)

        if form_reg.is_valid():
            cd = form_reg.cleaned_data
            if request.session['phone'] == cd['phone']:
                user = CustomUser.objects.create_user(
                    phone=cd['phone'],
                    password=cd['password'],
                    first_name=cd['first_name'],
                    surname=cd['surname'],
                    birthday=cd['birthday']
                )
                PhoneXcode.objects.filter(phone=cd['phone']).delete()
                return redirect('login')
            else:
                error = 'Неверно введен номер телефона!'


    form = Registration()
    return render(request, 'main/registration.html', {'form': form, 'error':error})






def time_table(request):

    today = datetime.datetime.today()
    end_day = today + datetime.timedelta(weeks=10)
    data_list = []

    while today < end_day:
        lessons = Lessons.objects.filter(data = today)
        data_list.append({'data':translat_in_russion(today.strftime('%d %B')),
                          'lessons': lessons})
        today += datetime.timedelta(days=1)
    
    return render(request, 'main/timetable.html', {'data':data_list})



def person_area(request):
    error = ''
    mes = ''
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':

            if 'Type-Post' in request.headers:
                json_string = request.body.decode('utf-8')
                body = json.loads(json_string)
                #удаление из расписания пользователя занятия, но не позже чем за 8 часов
                lesson = Lessons.objects.get(id=int(body['id']))
                today = datetime.datetime.today()
                lesson_data_str = lesson.data.strftime('%Y-%m-%d') + ' ' + lesson.time
                # перевод в объект datetime
                date_time = datetime.datetime.strptime(lesson_data_str, '%Y-%m-%d %H:%M')
                diff = date_time - today
                
                if int(diff.total_seconds()) > 8 * 3600:
                    TimeTable.objects.get(lesson=lesson, user=user).delete()
                    return HttpResponseRedirect('personArea')
                else:
                    mes = 'Нельзя отказаться от занятия менее чем за 8 часов.'
                # return HttpResponse(json.dumps(mes), content_type="text/plain", status=200)
                    return JsonResponse({'messeg': mes})
            else:
                
                #если номера совпадают, то просто вносим изменения в объект CustomUser
                if user.phone == request.POST.get('phone'):
                    CustomUser.objects.filter(id=user.id).update(surname=request.POST.get('surname'),
                                                                first_name=request.POST.get('first_name'),
                                                                    birthday=request.POST.get('birthday'))
                    return redirect('person')
                else:
                    error ='При смене телефона придется завести новый аккаунт!'
            
        
        time_table = TimeTable.objects.filter(user=user)
        subscription = Subscription.objects.filter(name=user)
        count_lesson = 'У вас нет абонемента. Для его приобретения напишите нам в социальных сетях.'
        if len(subscription) > 0:
            if subscription[0].count == 0:
                count_lesson = "У Вас закончился абонемент :("
            else:
                count_lesson = 'Занятия: ' + str(subscription[0].count)

        lst_lessons = []

        change_subcr_time_table(user, time_table)

        for el in time_table:
            lst_lessons.append(el.lesson)
        
        lst_lessons = sorted(lst_lessons, key=lambda x: x.data) 
        context = {
            'user':user,
            'user_date': user.birthday.strftime('%Y-%m-%d'),
            'lessons': lst_lessons, 
            'error':error,
            'subscript': count_lesson
        }


        return render(request, 'main/PersonArea.html', context)
    else:
        return redirect('login')






def change_password(request):
    error = ''
    phone = request.session.get('phone', None)

    if phone: #проверяем есть ли телефон в сессии если его нет, то юзер небыл на странице formPhone
        if request.method == 'POST':
            p1 = request.POST.get('p1')
            p2 = request.POST.get('p2')
            if p1 == p2:
                user = CustomUser.objects.get(phone=phone)
                user.set_password(p1)
                user.save()
                return redirect('login')
            else:
                error = 'Пароли не совпали!'
    else:
        return redirect('formPhone')


    return render(request, 'main/changePassword.html', {'error':error})

def error_page(request):
    return render(request, 'main/error.html')