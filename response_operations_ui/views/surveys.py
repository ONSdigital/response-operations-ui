import logging

from flask import render_template
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.controllers import survey_controllers


logger = wrap_logger(logging.getLogger(__name__))


@app.route('/', methods=['GET'])
def view_surveys():
    # survey_list = survey_controllers.get_surveys_list()
    survey_details = [
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef87",
            "shortName": "RSI",
            "longName": "Monthly Business Survey - Retail Sales Index",
            "surveyRef": "023",
            "legal_basis": "Statistics of Trade Act 1947"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "AIFDI",
            "longName": "Annual Inward Foreign Direct Investment Survey",
            "surveyRef": "062",
            "legal_basis": "Statistics of Trade Act 1947"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "AOFDI",
            "longName": "Annual Outward Foreign Direct Investment Survey",
            "surveyRef": "063",
            "legal_basis": "Statistics of Trade Act 1947"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "QIFDI",
            "longName": "Quarterly Inward Foreign Direct Investment Survey",
            "surveyRef": "064",
            "legal_basis": "Statistics of Trade Act 1947"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "QOFDI",
            "longName": "Quarterly Outward Foreign Direct Investment Survey",
            "surveyRef": "065",
            "legal_basis": "Statistics of Trade Act 1947"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "Sand&Gravel",
            "longName": "Quarterly Survey of Building Materials Sand and Gravel",
            "surveyRef": "066",
            "legal_basis": "Statistics of Trade Act 1947 - BEIS"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "Blocks",
            "longName": "Monthly Survey of Building Materials Concrete Building Blocks",
            "surveyRef": "073",
            "legal_basis": "Statistics of Trade Act 1947 - BEIS"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "Bricks",
            "longName": "Monthly Survey of Building Materials Bricks",
            "surveyRef": "074",
            "legal_basis": "Voluntary - BEIS"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "MWSS",
            "longName": "Monthly Wages and Salaries Survey",
            "surveyRef": "134",
            "legal_basis": "Statistics of Trade Act 1947"
        },
        {
            "id": "cb0711c3-0ac8-41d3-ae0e-567e5ea1ef88",
            "shortName": "PCS",
            "longName": "Public Corporations Survey",
            "surveyRef": "137",
            "legal_basis": "Voluntary Not Stated"
        }
    ]
    return render_template('surveys.html', survey_list=survey_details)


@app.route('/surveys/<short_name>', methods=['GET'])
def view_survey(short_name):
    survey_details = survey_controllers.get_survey(short_name)
    return render_template('survey.html',
                           survey=survey_details['survey'],
                           collection_exercises=survey_details['collection_exercises'])
