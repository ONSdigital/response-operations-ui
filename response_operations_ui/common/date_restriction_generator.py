def get_date_restriction_text(tag, events):
    return {
        "mps": [f"Must be before Go Live {_get_event_date_string('go_live', events)}"],
        "go_live": [f"Must be after MPS {_get_event_date_string('mps', events)}",
                    f"Must be before Return by {_get_event_date_string('return_by', events)}"],
        "return_by": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                      f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "exercise_end": [f"Must be after Return by {_get_event_date_string('return_by', events)}"],
        "reminder": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                     f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "reminder2": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                      f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "reminder3": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                      f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "ref_period_start": [f"Must be before Reference Period end {_get_event_date_string('ref_period_end', events)}"],
        "ref_period_end": [f"Must be after Reference Period start {_get_event_date_string('ref_period_start', events)}"]
    }.get(tag)


def _get_event_date_string(tag, events):
    try:
        return f"{events[tag]['day']} {events[tag]['date']} {events[tag]['time']}"
    except KeyError:
        return ""
