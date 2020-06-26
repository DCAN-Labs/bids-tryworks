from django.contrib import admin

from .models import DcmToBidsJson
from .models import Session
from .models import Subject

# Register your models here.
admin.register(Session, site='bids_tryworks')
admin.register(Subject, site='bids_tryworks')
admin.register(DcmToBidsJson, site='bids_tryworks')