from django.contrib import admin

from .models import DcmToBidsJson
from .models import Session
from .models import Subject

# Register your models here.
admin.register(Session, site='bidsgui2')
admin.register(Subject, site='bidsgui2')
admin.register(DcmToBidsJson, site='bidsgui2')