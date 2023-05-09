import urllib.parse
import requests
from .models import Subscription, Lessons, TimeTable
from django.db.models import F
import datetime



def translat_in_russion(string):
        dict_word = {
            'January': 'Января',
            'February': 'Февряля',
            'March':'Марта',
            'April':'Апреля',
            'May':'Мая',
            'June':'Июня',
            'July':'Июля',
            'August':'Августа',
            'September':'Сентября',
            'October':'Октября',
            'November':'Ноября',
            'December':'Декабря'
        }
        result = string.split(' ')
        return result[0] + ' ' + dict_word[result[1]]


def send_sms(user_phone: str, message: str, code):
    API_KEY = 'wBQX607lena'  #password
    LOGIN = 'elenabudyuk@yandex.ru'
    phone = '7' + user_phone
    sms_text = f'{message} {code}'
    params = {
        'login': LOGIN,
        'psw': API_KEY,
        'phones': phone,
        'mes': sms_text,
        'charset': 'utf-8'
    }
    url = 'https://smsc.ru/sys/send.php?' + urllib.parse.urlencode(params)
    sms_response = requests.get(url)
    response_json = str(sms_response.content)
    print(response_json)
    if response_json.find('ERROR = 9') == -1 and response_json.find('OK') == -1:
        return False
    else:
        return True

# проверяем есть записи на занятия у нашего пользователя
#  и если занятие уже прошло, то удаляем эту запись
def change_subcr_time_table(user, list_tab_time):

    today = datetime.datetime.today()

    for tab_time in list_tab_time:
        tad_time_user = tab_time.lesson.data.strftime('%Y-%m-%d') + ' ' + tab_time.lesson.time
        date_time = datetime.datetime.strptime(tad_time_user, '%Y-%m-%d %H:%M')

        if date_time < today:
            TimeTable.objects.get(id=tab_time.id).delete()
            Subscription.objects.filter(name=user).update(count = F('count') - 1)


#удаляем старые Lesson
def delete_old_lesson():
    today = datetime.datetime.today()

    Lessons.objects.filter(data__lt=today).delete()

