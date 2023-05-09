from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager




class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField('phone_number', unique=True, max_length=10)

    first_name = models.CharField('И.О.', max_length=30, blank=True)
    surname = models.CharField('Фамилия', max_length=30, blank=True)
    birthday = models.DateField('День рождения', default='2000-12-12')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.surname)



class Lessons(models.Model):
    data = models.DateField('Дата')
    time = models.CharField('Время', max_length=10, default='часы:минуты')
    duration = models.CharField('Продолжительность', max_length=50, default='60 мин')
    type_lesson = models.CharField('Тип занятия', max_length=200)
    trainer = models.CharField('Тренер', max_length=200)

    def __str__(self) -> str:
        return str(self.data) + ' ' + str(self.time)

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'


#абонемент для пользователя

class Subscription(models.Model):
    count = models.IntegerField('Кол занятий')
    name = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'Абонимент'
        verbose_name_plural = 'Абонименты'

# Расписание - запись юзера на занятие

class TimeTable(models.Model):
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.surname + " " + str(self.lesson.data) + ' - ' + self.lesson.time

    class Meta:
        verbose_name = 'Запись на зянатие'
        verbose_name_plural = 'Записи на зянатия'

# таблица где временно будет хранится код и номер на который будет отправлен этот код

class PhoneXcode(models.Model):

    phone = models.CharField('phone_number', max_length=10)
    xcode = models.CharField('xcode', max_length=10)

    class Meta:
        verbose_name = 'Код подверждения'

