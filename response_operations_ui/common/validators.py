from datetime import datetime


def valid_date_for_event(tag, form):
    form_datetime = datetime(int(form.year.data),
                             int(form.month.data),
                             int(form.day.data),
                             int(form.hour.data),
                             int(form.minute.data))
    tags_can_be_in_past = ("ref_period_start", "ref_period_end", "employment")

    if tag not in tags_can_be_in_past and form_datetime < datetime.now():
        form.errors["invalid_date"] = ["Selected date can not be in the past"]
        return False

    return True
