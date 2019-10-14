# coding: utf-8
import flask

blueprint = flask.Blueprint('filters', __name__)


@blueprint.app_template_filter()
def setAttribute(dictionary, key, value):
    dictionary[key] = value
    return dictionary
