from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
#first_name=None, surname=None, birthday=None 
    def create_user(self, phone, password=None, **kwargs):

        user = self.model(phone=phone, **kwargs)
        user.set_password(password)
        user.save()

        return user


    def create_superuser(self, phone, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password, **kwargs)
