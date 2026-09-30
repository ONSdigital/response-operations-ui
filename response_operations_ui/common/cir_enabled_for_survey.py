from flask import current_app as app


def is_cir_enabled_for_survey(survey_short_name):
    return app.config["CIR_ENABLED"] and survey_short_name not in app.config["CIR_SURVEY_EXCLUSIONS"]
