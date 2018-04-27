import logging

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.controllers import survey_controllers
from response_operations_ui.forms import EditSurveyDetailsForm
from response_operations_ui.forms import CreateSurveyDetailsForm
from response_operations_ui.common.mappers import map_collection_exercise_state, convert_events_to_new_format
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))

surveys_bp = Blueprint('surveys_bp', __name__,
                       static_folder='static', template_folder='templates/surveys')

def get_info_message(message_key):
    return {
        'survey_changed': "Survey details changed",
        'survey_created': "Survey created successfully"
    }[message_key]

@surveys_bp.route('/', methods=['GET'])
@login_required
def view_surveys():
    survey_list = survey_controllers.get_surveys_list()
    breadcrumbs = [{"title": "Surveys"}]

    message_key = request.args.get('message_key')

    if message_key:
        info_message  = get_info_message(message_key)
    else:
        info_message = None

    return render_template('surveys.html', info_message=info_message,
                           survey_list=survey_list, breadcrumbs=breadcrumbs)


@surveys_bp.route('/<short_name>', methods=['GET'])
@login_required
def view_survey(short_name):
    survey_details = survey_controllers.get_survey(short_name)
    breadcrumbs = [
        {
            "title": "Surveys",
            "link": "/surveys"
        },
        {
            "title": f"{survey_details['survey']['surveyRef']} {survey_details['survey']['shortName']}",
        }
    ]

    # Mapping backend states to frontend sates for the user
    for collection_exercise in survey_details["collection_exercises"]:
        collection_exercise['state'] = map_collection_exercise_state(collection_exercise['state'])
        if collection_exercise.get('events'):
            collection_exercise['events'] = convert_events_to_new_format(collection_exercise['events'])
        else:
            collection_exercise['events'] = None
    return render_template('survey.html',
                           survey=survey_details['survey'],
                           collection_exercises=survey_details['collection_exercises'],
                           breadcrumbs=breadcrumbs)


@surveys_bp.route('/edit-survey-details/<short_name>', methods=['GET'])
@login_required
def view_survey_details(short_name):
    survey_details = survey_controllers.get_survey(short_name)
    form = EditSurveyDetailsForm(form=request.form)

    return render_template('edit-survey-details.html', form=form, short_name=short_name,
                           legal_basis=survey_details['survey']['legalBasis'],
                           long_name=survey_details['survey']['longName'],
                           survey_ref=survey_details['survey']['surveyRef'])


@surveys_bp.route('/edit-survey-details/<short_name>', methods=['POST', 'GET'])
@login_required
def edit_survey_details(short_name):
    form = EditSurveyDetailsForm(form=request.form)
    if not form.validate():
        survey_details = survey_controllers.get_survey(short_name)
        return render_template('edit-survey-details.html', form=form, short_name=short_name, errors=form.errors,
                               legal_basis=survey_details['survey']['legalBasis'],
                               long_name=survey_details['survey']['longName'],
                               survey_ref=survey_details['survey']['surveyRef'],
                               survey_details=survey_details)

    else:
        form = request.form
        survey_controllers.update_survey_details(form.get('hidden_survey_ref'),
                                                 form.get('short_name'),
                                                 form.get('long_name'))
        return redirect(url_for('surveys_bp.view_surveys', short_name=short_name, message_key='survey_changed'))

@surveys_bp.route('/create', methods=['GET'])
@login_required
def show_create_survey():
    form = CreateSurveyDetailsForm(form=request.form)

    return render_template('create-survey.html', form=form)

@surveys_bp.route('/create', methods=['POST', 'GET'])
@login_required
def create_survey():
    form = CreateSurveyDetailsForm(form=request.form)
    if not form.validate():
        return render_template('create-survey.html', form=form, errors=form.errors.items(),
                               survey_ref=request.form.get('survey_ref'),
                               long_name=request.form.get('long_name'),
                               short_name=request.form.get('short_name'),
                               legal_basis=request.form.get('legal_basis'))
    else:
        logger.debug('create-survey form: {}'.format(form))
        try: 
            survey_controllers.create_survey(request.form.get('survey_ref'),
                                            request.form.get('short_name'),
                                            request.form.get('long_name'),
                                            request.form.get('legal_basis'))
            
            return redirect(url_for('surveys_bp.view_surveys', short_name=request.form.get('short_name'), message_key='survey_created'))
        except ApiError as err:
            # If it's conflict or bad request assume the service has returned a useful error message as the body of the response
            if err.status_code == 409 or err.status_code == 400:
                return render_template('create-survey.html', form=form, errors=[("", [err.message])],
                                    survey_ref=request.form.get('survey_ref'),
                                    long_name=request.form.get('long_name'),
                                    short_name=request.form.get('short_name'),
                                    legal_basis=request.form.get('legal_basis'))
            else:
                raise

