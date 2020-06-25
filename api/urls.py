from django.urls import include, path
from api.views import DcmToBidsJsonViewSet, SubjectViewSetAKA, ProgressIndicatorViewSet


urlpatterns = [
    path('api/', DcmToBidsJsonViewSet.as_view()),
    path('api/SubjectsAKA', SubjectViewSetAKA.as_view()),
    path('api/ProgressIndicator', ProgressIndicatorViewSet.as_view())
]
