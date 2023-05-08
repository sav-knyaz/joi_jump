from django.contrib import admin
from .models import Lessons, Subscription, CustomUser, TimeTable

# Register your models here.

admin.site.register(Subscription)
admin.site.register(CustomUser)
admin.site.register(Lessons)
admin.site.register(TimeTable)


