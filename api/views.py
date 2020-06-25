from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DcmToBidsJson, Subject, ProgressIndicator
from .serializers import DcmToBidsJsonSerializer, SubjectSerializer, ProgressSerializer
import tempfile
import json
import os
from django.db import DatabaseError, DataError
import time


from django.conf import settings


class DcmToBidsJsonViewSet(APIView):
    @staticmethod
    def get(self, request):
        dcm2bidsjsons = DcmToBidsJson.objects.all().order_by('name')
        serialized = DcmToBidsJsonSerializer(dcm2bidsjsons, many=True)
        return Response(serialized.data)

    def post(self, request):
        data = request.data["data"]
        filename = request.data["filename"].split("\\")[-1]
        filename = os.path.basename(filename)
        # checking if file has already been uploaded with filename
        query_set = DcmToBidsJson.objects.filter(name=filename)

        # if entry already exists in database select entry, but update it's attributes/objects
        if query_set:
            new_json = query_set[0]
            # still updating text at saved file location
            with open(os.path.join(settings.DCM2BIDS_FILES, filename), 'w+') as outfile:
                outfile.write(data)
            new_json.dcm_to_bids_txt = data
        # create new entry in db
        else:
            # Save into database 3 fields: filename, data (as text), data (as json)
            tempdir = tempfile.TemporaryDirectory()
            tempdir_file = os.path.join(tempdir.name, filename)
            with open(tempdir_file, "w+") as outfile:
                outfile.write(data)

            with open(os.path.join(settings.DCM2BIDS_FILES, filename), 'w+') as outfile:
                outfile.write(data)

            new_json = DcmToBidsJson(
                dcm_to_bids_txt=data,
                dcm_to_bids_file=tempdir_file,
                name=filename,
                path=os.path.join(settings.DCM2BIDS_FILES, filename)
            )

        pk_for_new_json = new_json.pk
        new_json.save()
        request.data['uploaded_config_pk'] = pk_for_new_json

        return Response(request.data)


class SubjectViewSetAKA(APIView):
    # queries database for subject(s) provided in list via PK
    @staticmethod
    def get(request):
        try:
            subjects_returned = Subject.objects.filter(pk__in=request.data['Subjects'])
            serialized = SubjectSerializer(subjects_returned, many=True)
            return Response(serialized.data)
        except KeyError:
            subjects_returned = Subject.objects.all()
            return Response(SubjectSerializer(subjects_returned, many=True).data)

    @staticmethod
    def post(request):
        # given a post request containing a dictionary of pks as keys and new names as values
        # update the aka field of those subjects
        successfully_updated = {}
        SubjectID = request.data['SubjectID']
        SubjectAKA = request.data['SubjectAKA']
        try:
            subject = Subject.objects.get(SubjectID=SubjectID)
            subject.AKA = SubjectAKA
            subject.save()
            successfully_updated[SubjectID] = {
                    'updated': True,
                    'error': 'Null',
            }
        except (DatabaseError, DataError) as err:
            successfully_updated[SubjectID] = {'updated': False, 'error': str(err)}
        return Response(json.dumps(successfully_updated))


class ProgressIndicatorViewSet(APIView):
    @staticmethod
    def get(request):
        one_hour_window = time.time() - 3600
        conversions = ProgressIndicator.filter(time_started__level__gt=one_hour_window)
        serialized = ProgressSerializer(conversions, many=True)
        try:
            return Response(serialized.data)
        except KeyError:
            return Response('{}')
    
    @staticmethod
    def post(request):
        """
        request data should look like
        {
            'path1/': {
                        'number_of_sessions': 10,
                        'number_completed'
                    }, 
            'path2/': {
                       'number_of_sessions': 20, 
                       'number_completed': 10}
                       }
        """
        data = request.data['data']
        on_going_conversions = []
        for path, progress_fields in data.items():
            progress = ProgressIndicator.objects.get_or_create(conversion_output_path=path)
            progress.number_of_sessions = progress_fields['number_of_sessions']
            if progress_fields['number_completed'] > progress.number_completed:
                progress.number_completed = progress_fields['number_completed']
            on_going_conversions.append(progress)
        return Response(ProgressSerializer(on_going_conversions, many=True))


