#!/usr/bin/python
import argparse
import datetime
import requests
from os import abort

from dateutil import tz


def parse_args():
    parser = argparse.ArgumentParser(description='Align collection exercise events and rules')
    parser.add_argument("url", help="Collection exercise service URL")
    parser.add_argument("user", help="Basic auth user")
    parser.add_argument("password", help="Basic auth password")
    return parser.parse_args()


def update_event(collex_id, event_tag, date, url, user, password):
    path = "/collectionexercises/{id}/events/{tag}".format(id=collex_id, tag=event_tag)
    response = requests.put(url+path,
                            data=date,
                            auth=(user, password),
                            headers={'content-type': 'text/plain'})

    status_code = response.status_code

    if status_code != 204:
        detail_text = response.text
        print("{} <= {} ({})".format(status_code, date, detail_text))


def get_collection_exercises(user, password, url):
    print(url)
    response = requests.get(url + "/collectionexercises", auth=(user, password))

    status_code = response.status_code

    if status_code == 200:
        ces = response.json()
        print("{} <= {} collection exercises retrieved".format(status_code, len(ces)))
        return ces

    print("{} <= {}".format(status_code, response.text))
    abort()


def is_mandatory_event(event):
    mandatory_events = ['mps', 'go_live', 'reminder', 'reminder1', 'reminder2']
    return event['tag'] in mandatory_events


def align_events_and_rules(collection_exercises, user, password, url):
    for collection_exercise in collection_exercises:
        print("\nPROCESSING COLLECTION_EXERCISE: {} {} {} {}".format(collection_exercise['name'],
                                                                     collection_exercise['exerciseRef'],
                                                                     collection_exercise['state'],
                                                                     collection_exercise['id']))

        for event in collection_exercise['events']:
            if not is_mandatory_event(event):
                continue

            formatted_new_date = change_time_to_9_am(event['timestamp'])

            print("EVENT: {} {} currently: {} changing to: {}".format(event['tag'],
                                                                      event['id'],
                                                                      event['timestamp'],
                                                                      formatted_new_date))

            update_event(collex_id=collection_exercise['id'],
                         event_tag=event['tag'],
                         date=formatted_new_date,
                         url=url,
                         user=user,
                         password=password)


def change_time_to_9_am(event_timestamp):
    date_format = '%Y-%m-%dT%H:%M:%S.%f'
    date = datetime.datetime.strptime(event_timestamp[:-1], date_format)
    london_timezone = tz.gettz('Europe/London')
    new_date = date.replace(hour=9, minute=0, second=0, microsecond=0, tzinfo=london_timezone)
    return new_date.isoformat(timespec='milliseconds')


if __name__ == '__main__':
    args = parse_args()

    url = args.url
    user = args.user
    password = args.password

    collection_exercises = get_collection_exercises(user=user, password=password, url=url)

    align_events_and_rules(collection_exercises=collection_exercises, user=user, password=password, url=url)

    print("Finished aligning events and rules")
