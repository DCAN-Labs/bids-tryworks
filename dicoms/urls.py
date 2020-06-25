from django.urls import path, re_path
from . import views
import threading

import time
from utils.docker_check import am_i_in_docker

from utils.dir_watch import DicomWatcher, SessionWatcher
if not am_i_in_docker():
    from bids-tryworks.settings import BASE_DICOM_DIR
else:
    from bids-tryworks.docker import BASE_DICOM_DIR

urlpatterns = [
    path('', views.search_subjects, name='allsubjects'),
    path('search/', views.search_subjects, name='search'),
    path('search_results/', views.search_results, name='search_results'),
    path('search_selection/', views.search_selection, name='search_selection'),
    path('convert_builder/', views.convert_subjects, name='convert_builder'),
    path('convert/', views.convert, name='convert'),
    path('convert_builder/', views.create_dcm2bids_config, name='create_dcm2bids_config'),
    path('tester/', views.search_results, name='tester')
]



