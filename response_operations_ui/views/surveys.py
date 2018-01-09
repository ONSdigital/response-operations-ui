import logging

from flask import render_template
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers


logger = wrap_logger(logging.getLogger(__name__))


@app.route('/', methods=['GET'])
def view_surveys():
    survey_list = survey_controllers.get_surveys_list()
    return render_template('surveys.html', survey_list=survey_list)


@app.route('/surveys/<short_name>', methods=['GET'])
def view_survey(short_name):
    survey_details = survey_controllers.get_survey(short_name)
    return render_template('survey.html',
                           survey=survey_details['survey'],
                           collection_exercises=survey_details['collection_exercises'])


@app.route('/surveys/<short_name>/<period>', methods=['GET'])
def view_collection_exercise(short_name, period):
    # ce_details = collection_exercise_controllers.get_collection_exercise(short_name, period)
    ce_details = {
      "collection_exercise": {
        "actualExecutionDateTime": "2017-11-10T12:14:41.768+0000",
        "actualPublishDateTime": "2017-11-10T12:16:28.509+0000",
        "caseTypes": [
          {
            "actionPlanId": "e71002ac-3575-47eb-b87f-cd9db92bf9a7",
            "sampleUnitType": "B"
          },
          {
            "actionPlanId": "0009e978-0932-463b-a2a1-b45cb3ffcb2a",
            "sampleUnitType": "BI"
          }
        ],
        "executedBy": None,
        "exerciseRef": "221_201712",
        "id": "14fb3e68-4dca-46db-bf49-04b84e07e77c",
        "name": "000000",
        "periodEndDateTime": "2017-09-15T22:59:59.000+0000",
        "periodStartDateTime": "2017-09-14T23:00:00.000+0000",
        "scheduledEndDateTime": "2018-06-29T23:00:00.000+0000",
        "scheduledExecutionDateTime": "2017-09-10T23:00:00.000+0000",
        "scheduledReturnDateTime": "2017-10-06T00:00:00.000+0000",
        "scheduledStartDateTime": "2017-09-11T23:00:00.000+0000",
        "state": "PUBLISHED",
        "surveyId": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87"
      },
      "survey": {
        "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
        "longName": "Business Register and Employment Survey",
        "shortName": "BRES",
        "surveyRef": "221"
      },
      "events": {
          "mps": {
              "day": "Mon",
              "date": "15 May 1993",
              "time": "12:00 GMT"
          }
      }
    }
    return render_template('collection-exercise.html',
                           survey=ce_details['survey'],
                           ce=ce_details['collection_exercise'],
                           events=ce_details['events'])
