from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.utils import timezone, dateparse
from django.utils.datastructures import MultiValueDictKeyError
from django.core import serializers
import time


from django.template.defaultfilters import slugify
# importing path to project
from django.conf import settings
# collecting paths from settings env file
import dotenv

from django.views.decorators.csrf import csrf_exempt
from dicoms.forms import SearchForm, make_conversion_form, ConversionForm2
from dicoms.models import Subject, Session, Series, DcmToBidsJson, ProgressIndicator
from string import ascii_letters, digits

from utils.transfer import login_and_sync

# standard library imports
from os.path import basename, normpath, dirname, realpath, join
from ast import literal_eval
import json
from operator import itemgetter
import dcm2bids
import os

dotenv.load_dotenv(dotenv.find_dotenv())

FULL_PATH_TO_DICOMS_SOURCE_FOLDER = os.environ['BASE_DICOM_DIR']
FULL_PATH_TO_DCM2BIDS_FILES = os.environ['DCM2BIDS_FILES']


# for doing processing asyncronously, timeouts often occur otherwise

DICOMS_APP_FOLDER = dirname(realpath(__file__))
PROCESSED_BIDS = settings.CONVERTED_FOLDER
EPOCH_TIME = '1970-01-01T00:00:00Z'  # shouldn't have any dicoms older than this.


# Create your views here.
def get_all_subjects(request):
    """
    This doesn't really do anything, you should probably delete it.
    :param request:
    :return:
    """
    all_subjects = Subject.objects.all().order_by('SubjectID')
    context_dict = {'all_subjects': all_subjects}
    serialized_context = serialize_context_dict(context_dict)
    context_dict['serialized'] = serialized_context
    return render(request, 'dicoms/index.html', context_dict)


def search_subjects(request):
    """
    This is our search view, at present it collects queries relating to:
        - Subject ID
        - Study Name
        - Date Range Start
        - Date Range Start
    Then validates these entries, after which it redirects to the search
    results view.
    :param request:
    :return: Redirect to search results if search button is pressed and form fields
    are valid or renders this view again if this request is not POST
    """

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.save(commit=False)
            search.subject_search = request.POST['subject_search']
            search.study_search = request.POST['study_search']

            # if user supplied a starting date and it's valid
            # or if  they didn't at all.
            date_fields_provided = False
            if request.POST['date_range_alpha'] and \
                    dateparse.parse_date(request.POST['date_range_alpha']):
                with_tz = dateparse.parse_date(request.POST['date_range_alpha'])
                search.date_range_alpha = with_tz
                date_fields_provided = True
            else:
                search.date_range_alpha = dateparse.parse_datetime(EPOCH_TIME)

            # similar logic for and end date, if not is supplied defaults to now
            if request.POST['date_range_omega'] and \
                    dateparse.parse_date(request.POST['date_range_omega']):
                with_tz = dateparse.parse_date(request.POST['date_range_omega'])
                search.date_range_omega = with_tz
                date_fields_provided = True
            else:
                search.date_range_omega = timezone.now()

            # if no file is specified pass
            try:
                if request.FILES['multi_search']:
                    search.multi_search = request.FILES['multi_search']
            except MultiValueDictKeyError:
                pass

            # saving search to our database, not sure how necessary this is, but hey
            # why not?
            search.save()

            # If the user passes in a text file to the search with a list of
            # subjects do the following
            if search.multi_search:
                readit = search.multi_search.read()

                decoded = readit.decode('utf-8')
                subject_list = decoded.splitlines()
                list_search_queryset = Session.objects.none()
                for subject in subject_list:
                    one_from_list_queryset = Session.objects.filter(Subject__SubjectID__contains=subject,
                                                                    SessionDate__range=[search.date_range_alpha,
                                                                                  search.date_range_omega])
                    list_search_queryset = one_from_list_queryset | list_search_queryset
            else:
                list_search_queryset = Session.objects.none()

            # retrieving sessions via subject id's, if else is necessary to avoid returning
            # all sessions. '' returns every session.
            if search.subject_search:
                subject_queryset = Session.objects.filter(Subject__SubjectID__contains=search.subject_search,
                                                          SessionDate__range=[search.date_range_alpha,
                                                                              search.date_range_omega])
            else:
                subject_queryset = Session.objects.none()

            # retrieving sessions via StudyDescription, if else is necessary to avoid returning
            # all sessions. '' returns every session.
            if search.study_search:
                study_queryset = Session.objects.filter(StudyDescription__contains=search.study_search,
                                                        SessionDate__range=[search.date_range_alpha,
                                                                            search.date_range_omega])
            else:
                study_queryset = Session.objects.none()

            # if user provides a date
            if date_fields_provided and not search.subject_search and not search.multi_search \
                    and not search.study_search:
                date_set = Session.objects.filter(SessionDate__range=[search.date_range_alpha,
                                                                      search.date_range_omega])
            else:
                date_set = Session.objects.none()
            # combining querysets is equivalent to set(subject_queryset + study_queryset)

            full_set = subject_queryset | study_queryset | list_search_queryset | date_set
            full_set = full_set.order_by("Subject", "SessionDate")

            # dictionary for search results
            search_results_dict = {}
            for each in full_set:
                search_results_dict[each.pk] = {
                    'SubjectID': each.Subject.SubjectID,
                    'SubjectAKA': each.Subject.AKA,
                    'Date': each.SessionDate.strftime('%Y-%m-%d'),
                    'Path': each.Path,
                    'Session': each.pk,
                    'Series': []  
                }

                for series in each.series_set.all():
                    search_results_dict[each.pk]['Series'].append({  # [series.pk] = {
                        'SeriesDescription': series.SeriesDescription,
                        'StudyDescription': series.StudyDescription,
                        'SeriesNumber': series.SeriesNumber,
                        'SeriesDate': series.SeriesDate.strftime('%Y-%m-%d'),
                        'ImageType': series.ImageType,
                        'AcquisitionTime': series.AcquisitionTime
                    })

            # populating our context dictionary
            context = {
                'search': search,
                'sessions': full_set,
                'session_series': json.dumps(search_results_dict).replace("'", "\\'")
            }
            serialized = serialize_context_dict({'sessions': context['sessions']})
            context['serialized'] = serialized
            #context['results_for_search_select'] = serialize_context_dict({'results_for_search_select'}: search_results_dict)
            # redirecting/rendering the results to it's own html.
            next_page = "dicoms/search_results.html" if full_set else "dicoms/empty_search.html"
            return render(request, next_page, context)
    else:
        form = SearchForm()

    return render(request, 'dicoms/search.html', {'form': form,
                                                  'dicom_source': FULL_PATH_TO_DICOMS_SOURCE_FOLDER})


def search_results(request):
    if request.method == "GET":
        return render(request, "dicoms/search_results.html")
    else:
        return render(request, "dicoms/search_results.html")


def extract_most_complete_series_names(sessions):
    """
    Presently, the user will have to choose a subject that has the most
    representative number of scans to constitute a 'complete' series.
    This function determines completeness based on the number of unique
    series that a subject possesses.

    It would be better if the most complete series/scan list was
    gotten by looking through every subject and extracting unique
    series from that list, but for this moment we're relying on the user
    to make a good choice.
    :param sessions: A queryset of selected sessions passed in from a
    search
    :return: a single session's PK where that session contains the most
    complete ((although it might be better to
    return the session entirely, saves ourselves 1 query)
    """
    subject_and_series = {}
    for session in sessions:
        series = session.series_set.all()
        list_of_series = []
        for each in series:
            list_of_series.append(each.Path)
        cleaned_series = [basename(normpath(single_series)) for single_series in list_of_series]
        cleaned_series_set = set(cleaned_series)
        cleaned_series = list(cleaned_series_set)
        subject_and_series[session.pk] = cleaned_series

    sorted_by_num_series = sorted(subject_and_series,
                                  key=lambda k: len(subject_and_series[k]),
                                  reverse=True)
    if sorted_by_num_series:
        return sorted_by_num_series[0]
    else:
        return None


def extract_unique_series(sessions):
    """
    Presently, the user will have to choose a subject that has the most
    representative number of scans to constitute a 'complete' series.
    This function determines completeness based on the number of unique
    series that a subject possesses.

    It would be better if the most complete series/scan list was
    gotten by looking through every subject and extracting unique
    series from that list, but for this moment we're relying on the user
    to make a good choice.
    :param sessions: A queryset of selected sessions passed in from a
    search
    :return: a single session's PK where that session contains the most
    complete ((although it might be better to
    return the session entirely, saves ourselves 1 query)
    """
    subject_and_series = {}
    series_description = []
    storage_dict = {}
    series_number = {}
    for session in sessions:
        series = session.series_set.all()
        list_of_series = []
        # this dictionary is being used to store k: series desc, v: series primary key
        # it's necessary to divorce the two and easily reunite them later.
        # this is done solely so that when referring to html elements id's in the templates
        # that there are only numbers, no invalid characters referenced (it's fine for
        # rendering, but jquery does not like invalid chars).

        for each in series:
            list_of_series.append(each.SeriesDescription)
            storage_dict[each.SeriesDescription] = each.pk
            series_number[each.SeriesDescription] = each.SeriesNumber

        series_description = series_description + list_of_series

    unique_series = list(set(series_description))

    unique_w_pk = [(series, storage_dict[series], series_number[series]) for series in unique_series]
    unique_w_pk.sort(key=lambda tup: tup[2])

    return unique_w_pk


def search_selection(request):
    """
    This view allows the user to select multiple subjects for either
    conversion to bids format or for the generation of a conversion file
    for dcm2bids (note as of now it defaults to only choosing the subject
    with the most "complete" series, however this behavior can be modified
    easily in the extract series def within this module.
    :param request:
    :return: A redirect to a dcm2bids conversion page where the user is able
    to either pick a dcm2bids config file for the subjects they've chosen or
    generate one with the use of drop downs./home/exacloud/lustre1/fnl_lab/projects/INFANT/GEN_INFANT/masking_test/
    """
    if request.method == 'POST':
        context = {}
        # getting the primary keys of the sessions selected from the
        # previous view
        selected_subjects = request.POST.getlist("search_selection")
        if selected_subjects:
            request.session['selected_subjects'] = selected_subjects

        # retrieving the sessions with another query, this is possibly inefficient
        # but it works for now
        sessions = Session.objects.filter(pk__in=selected_subjects)

        context['sessions'] = sessions
        if context['sessions']:
            request.session['sessions'] = list(context['sessions'].values_list('pk', flat=True))
        # here we collect the session with the most series/scans in it
        session_id = extract_most_complete_series_names(sessions)

        # getting unique series descriptions
        unique_series = extract_unique_series(sessions)
        # context['session'] = Session.objects.get(pk=session_id)
        context['session'] = get_object_or_404(Session, pk=session_id)
        if context['session']:
            request.session['session'] = session_id
        # next collect every series corresponding to that session
        context['series'] = Series.objects.filter(Session=session_id)
        context['unique_series'] = unique_series
        if context['series']:
            request.session['series'] = list(context['series'].values_list('pk', flat=True))
            request.session['unique_series_description'] = context['unique_series']
        # keeping track of our selected subjects from the earlier search for
        # the next view.
        context['search_selection'] = selected_subjects
        serialized = serialize_context_dict(context)
        context['serialized'] = serialized
        return redirect('/dicoms/convert_builder/')

    else:
        context = {}
        serialized = serialize_context_dict(context)
        context['serialized'] = serialized
        return render(request, "dicoms/search.html", context)
        # return render(request, "dicoms/search.html", context)


def convert_subjects(request):  # , session_id):
    """
    This view directs the user to the page where the user creates a
    dicom configuration for their study/subject.
    :param request:
    :param : A context dictionary containing subjects,
    sessions, series, a list of primary keys corresponding with the previous
    selection of sessions that that person wishes to convert.
    :return:
    """
    date = timezone.localtime(timezone.now()).isoformat()
    bidspec = json.load(open(join(DICOMS_APP_FOLDER,"bids_spec.json")))
    scan_choices = bidspec['anat'] + bidspec['func'] + bidspec['fmap'] + bidspec['meg'] + bidspec['dwi'] + bidspec['beh']

    scan_choices.sort()
    # ADDING IGNORE AS DEFAULT CHOICE
    scan_choices.insert(0, 'IGNORE')
    scan_choices_list = []
    scan_choices_list.append({'ana': bidspec['anat']})
    scan_choices_list.append({'func': bidspec['func']})
    scan_choices_list.append({'fmap': bidspec['fmap']})
    scan_choices_list.append({'dwi': bidspec['dwi']})
    scan_choices_list.append({'beh': bidspec['beh']})
    scan_choices_list.append({'meg': bidspec['meg']})

    # loading previously user dcm2bids configs

    dcm2bids_jsons = DcmToBidsJson.objects.all()
    dcm2bids_jsons_in_dict = {}
    for each in dcm2bids_jsons:
        dcm2bids_jsons_in_dict[each.pk] = {'name': each.name, 'json': each.dcm_to_bids_txt}

    context = {'date': date, 'scan_choices_list': scan_choices_list, 'scan_choices': scan_choices,
               'required': json.dumps(bidspec['required']), 'bidspecJson': json.dumps(scan_choices),
               'test': json.dumps(bidspec), 'output_path': settings.CONVERTED_FOLDER,
               'dcm2bids_jsons': dcm2bids_jsons_in_dict}

    for k, v in request.session.items():
        if k == 'sessions':
            context['sessions'] = Session.objects.filter(pk__in=v)
        elif k == 'series':
            series = Series.objects.filter(pk__in=v)
            # trimming off only the informative part of the path
            trimmed = []
            series_description = []
            for each in series:
                trimmed.append({'folder': basename(normpath(each.Path)),
                                'SeriesDescription': each.SeriesDescription})
            # sorting series on folder path
            trimmed = sorted(trimmed, key=itemgetter('folder'))

            context['series'] = trimmed
        elif k == 'selected_subjects':
            context['subjects'] = Subject.objects.filter(pk__in=v)
        elif k == 'unique_series_description':
            context['unique_series_description'] = v

    if request.method == 'POST':
        # load conversion page
        series_pks = request.POST.getlist('pk')
        series_descriptions = request.POST.getlist('series')
        required_labels = request.POST.getlist('required_label')
        custom_labels = request.POST.getlist('custom_label')
        modality_choices = request.POST.getlist('modality')
        image_type = ['' for entry in series_pks]
        conf_filename = request.POST['dcm2bids_conf_filename']
        session_pks = request.session.get('selected_subjects')
        output_folder = request.POST['output_folder']

        for index, pk in enumerate(series_pks):
            """Here we're getting the image types/descriptions from each scan/series"""
            series_image_type = Series.objects.get(pk=pk).ImageType
            image_type[index] = series_image_type

        # if user wants to create a new config or reuse an old one, examin this var to determine.
        make_new_boolean = request.POST['make_new_boolean']
        use_uploaded_boolean = request.POST['use_uploaded_boolean']
        if make_new_boolean == "True" and use_uploaded_boolean == "False":
            config = generate_dcm2bids_config(
                custom_labels,
                image_type,
                modality_choices,
                required_labels,
                series_descriptions,
                conf_filename)
        elif make_new_boolean == "False" and use_uploaded_boolean != "False":
            config = DcmToBidsJson.objects.get(pk=int(request.POST['use_uploaded_boolean']))
        else:
            config = DcmToBidsJson.objects.get(pk=int(request.POST['old_config_pk']))


        # collecting vars for scp. Host, User, Path, etc.
        transfer_kwargs = {
            'source': os.path.join(settings.CONVERTED_FOLDER, output_folder),
            'destination': request.POST['remote-path'],
            'user': request.POST['remote-user'],
            'host': request.POST['remote-server'],
            'password': request.POST['remote-password'],
        }

        convert(session_pks, config, output_folder, transfer_kwargs, compression='y')

        # moving files locally or across to a different server
        #sync_thread = threading.Thread(target=login_and_sync, kwargs=transfer_kwargs)
        #sync_thread.start()

        # passing the output path into our context variable for the next page.
        context['host'] = transfer_kwargs['host']
        context['user'] = transfer_kwargs['user']
        context['source'] = transfer_kwargs['source']
        context['destination'] = transfer_kwargs['destination']

        # serializing objects in context dictionary into json
        serialized = serialize_context_dict(context)
        context['serialized'] = serialized
        return render(request, "dicoms/convert_page.html", context)
    else:
        # reload this page without any selected subjects.
        context['path_to_dcm2bids_jsons'] = FULL_PATH_TO_DCM2BIDS_FILES
        serialized = serialize_context_dict(context)
        context['serialized'] = serialized
        context['dicom_source'] = FULL_PATH_TO_DICOMS_SOURCE_FOLDER
        return render(request, "dicoms/convert_builder.html", context)


def generate_dcm2bids_config(custom_labels,
                             image_types,
                             modality,
                             required_labels,
                             series_descriptions,
                             conf_filename=None):
    """Function combines input lists to create a dictionary and then a json
    conforming to the dcm2bids template requirements. First combines elements
    from the four input lists into a dictionary, and then creates a json.

    Some basic bids format handling will be done here, but eventually this
    input error handling  (no / _ etc etc certain characters in bids) at the
    form input level.

    :param modality: user selected modality for scan type.
    :param series_descriptions: a list of all unique series obtained from the subject search
    :param required_labels: list of required labels (eg task- for bold and dir- for epi)
    :param custom_labels: These are the user defined labels to describe each session
    :param image_types: Image types collected form series/scans. I'm not sure if dcm2bids needs
    these, but atm I'm including them
    :return: a correctly formatted dcm2bids conf dictionary to later be turned into a json
    """
    config = {"descriptions": []}
    with open(join(DICOMS_APP_FOLDER, "bids_spec.json")) as infile:
        bidspec_full = json.load(infile)
        bidspec = {}
        for key in bidspec_full:
            if key == "anat" or key == "func" or key == "dwi" or key == "fmap" or key == "beh":
                bidspec[key] = bidspec_full[key]

    for index, entry in enumerate(modality):
        tempdict = {}
        for key, value in bidspec.items():
            if modality[index] in value:
                dataType = key
                break
            else:
                dataType = None

        if modality[index] != "IGNORE" and dataType:
            tempdict["dataType"] = dataType
            tempdict["modalityLabel"] = modality[index]

            if custom_labels[index] != "":
                tempdict["customLabels"] = required_labels[index] + custom_labels[index]

            if series_descriptions[index] != "":
                cleaned_series_description = series_descriptions[index].split('\r')[0]
                cleaned_series_description = cleaned_series_description.replace(' ', '_')

                tempdict["criteria"] = {"SeriesDescription": cleaned_series_description,

                                        "ImageType": literal_eval(image_types[index])}

            config["descriptions"].append(tempdict)

    dcm2bids_folder = settings.DCM2BIDS_FILES
    # checking on whether or not a folder exists that stores the config jsons
    if not os.path.exists(dcm2bids_folder):
        os.makedirs(dcm2bids_folder)

    # writing json to disk
    # create json from config dictionary using pretty printing:
    if not conf_filename:
        dcm2bids_file = os.path.join(dcm2bids_folder, str(timezone.now().isoformat() + ".json"))
    else:
        dcm2bids_file = os.path.join(dcm2bids_folder, conf_filename + ".json")
    with open(dcm2bids_file, 'w') as outfile:
        output = json.dumps(config, indent=4, separators=(',', ': '))
        print(output, file=outfile)

    dcm2bids_db_entry = DcmToBidsJson(name=os.path.basename(dcm2bids_file),
                                      path=dcm2bids_file,
                                      dcm_to_bids_txt=json.dumps(config, indent=4, separators=(',', ': ')),
                                      dcm_to_bids_file=dcm2bids_file)
    dcm2bids_db_entry.save()
    return dcm2bids_db_entry


@csrf_exempt
def create_dcm2bids_config(request):
    """
    This function exists as handler to be called the javascript in our convert builder
    page. This view will either build the conversion form from some of the information
    gleaned via jquery/js via some queries to the database to retrieve info. Or it will
    simply take in a json from jquery/js and populate a DcmToBidsJson and associate it
    with the requisite sessions that it's been created for.

    Edit: We're going to pass everything we collect here to python and do the work in
    this view. There's no reason to fight javascript unless you have to.
    :param request:
    :return:
    """

    if request.method == 'POST':
        return HttpResponse("you posted to create_dcm2bids_config")
    else:
        return HttpResponse("you get'd or something else to create_dcm2bids_config")


def convert(selected_session_pks, config, output_dir=settings.CONVERTED_FOLDER, transfer_kwargs=None, compression='i'):
    """
    This is the bit that actually does the work of converting dicoms into bids
    formatted nifti's and their corresponding sidecar.jsons. It takes three
    arguments and then passes those arguments to a dcm2bids to do the conversion.
    :param selected_session_pks: These are the primary keys for each session
    that the user has selected to be converted. An individual session corresponds
    to all of the imaging data acquired during a single visit (session, tautological
    description I know).
    :param config: The dcm2bids conf file that the user has created w/ via selecting
    the appropriate modalities, choosing custom labels, and selecting which scans
    to includ exclude in their conversion.
    :param output_dir: The directory where the output from the conversion will
    be stored.
    :return:
    """

    output_dir = os.path.join(settings.CONVERTED_FOLDER, output_dir)

    try:
        if os.path.exists(output_dir):
            pass
        else:
            os.makedirs(output_dir)
    except (PermissionError, FileExistsError):
        raise

    # querying the database for all of the sessions the user selected.
    selected_sessions = Session.objects.filter(pk__in=selected_session_pks)

    # converting
    for session in selected_sessions:
        # get participant ID. parse metadata to strip characters
        allowed = ascii_letters + digits
        session_subject = Subject.objects.get(SubjectID=session.Subject)
        if session_subject.AKA:
            participant_ID = ''.join([a for a in str(session_subject.AKA) if a in allowed])
        else:
            participant_ID = ''.join([a for a in str(session_subject.SubjectID) if a in allowed])
        
        # get session_ID. make sure it's in the format YYYYMMDD
        session_ID = session.SessionDate.strftime("%Y%m%d")

        # building kwargs to pass to dcm2bids
        command_args = {"dicom_dir": session.Path,
                        "participant": participant_ID,
                        "config": config.path,
                        "output_dir": output_dir,
                        "session": session_ID,
                        "clobber": False,
                        "forceDcm2niix": True,
                        "compression": compression}

        # making magic happen here
        print(selected_session_pks)
        print(config)
        print(output_dir)

        

        dcm2bids_conversion = dcm2bids.Dcm2bids(**command_args)
        dcm2bids_conversion.run()

        # if provided with transfer args, moving across server or locally
        if transfer_kwargs:
            login_and_sync(**transfer_kwargs)
        
        # record conversion event/create progress object on completion
        progress = ProgressIndicator.objects.get_or_create(conversion_output_path=output_dir)
        if progress.time_started > time.time() - 3600:
            progress.number_of_sessions = len(selected_sessions)
            progress.number_completed = progress.number_completed + 1 

    return output_dir


def serialize_context_dict(dictionary: dict) -> str:
    temp_dict = {}
    try:
        for key, value in dictionary.items():
            isnt_model = False
            try:
                # if object is a django queryset or model type object
                if 'models' in str(type(value)):

                    # serializing object into string
                    first_pass = serializers.serialize("json", value)
                    # passing object back into a dictionary, we do this so we have access to the
                    # model/object attributes that were previously hidden within the class (well hidden to non-python)
                    back_to_dict = json.loads(first_pass)
                    temp_dict[key] = back_to_dict
                else:
                    isnt_model = True
            except (TypeError, AttributeError) as err:
                if err is TypeError and "models" in str(type(value)):
                    value = str(value)
                isnt_model = True

            if isnt_model:
                try:
                    # I think there is a smarter way to do this
                    temp_values = json.dumps(value)
                    temp_dict[key] = json.loads(temp_values)
                except TypeError:
                    if "model" in str(type(value)):
                        temp_dict[key] = str(value)
                    else:
                        temp_dict[key] = value
                    pass

    except AttributeError as err:
        # TODO UHHH this undoes all of the work you did above. But I still can't figure out
        # TODO why this case is even triggering.
        print(err)
    return json.dumps(temp_dict)
