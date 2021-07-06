from datetime import datetime

from wtforms import ValidationError

from config import Config


def valid_date_for_event(tag, form):
    form_datetime = datetime(
        int(form.year.data), int(form.month.data), int(form.day.data), int(form.hour.data), int(form.minute.data)
    )
    tags_can_be_in_past = ("ref_period_start", "ref_period_end", "employment")

    if not Config.TEST_MODE:
        if tag not in tags_can_be_in_past and form_datetime < datetime.now():
            raise ValidationError("Selected date can not be in the past")
