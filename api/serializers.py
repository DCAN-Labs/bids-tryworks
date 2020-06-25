from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import DcmToBidsJson, Subject, ProgressIndicator


class DcmToBidsJsonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DcmToBidsJson
        fields = ('name', 'sessions', 'path', 'dcm_to_bids_txt', 'dcm_to_bids_file')


class SubjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subject
        fields = ('SubjectID', 'AKA', 'slug')


class ProgressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProgressIndicator
        fields = ('conversion_output_path',
                  'number_of_sessions',
                  'number_completed')
