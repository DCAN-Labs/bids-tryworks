from django.contrib import admin

from dicoms.models import DcmToBidsJson
from dicoms.models import Series
from dicoms.models import Session
from dicoms.models import Subject

admin.site.register(Session)
admin.site.register(Subject)
admin.site.register(DcmToBidsJson)
admin.site.register(Series)
