import logging

import requests
from flask import current_app as app
from requests.exceptions import HTTPError, RequestException
from structlog import wrap_logger

from response_operations_ui.controllers.survey_controllers import get_survey_by_id
from response_operations_ui.exceptions.exceptions import ApiError, UpdateContactDetailsException
from response_operations_ui.forms import EditContactDetailsForm


logger = wrap_logger(logging.getLogger(__name__))


def get_party_by_ru_ref(ru_ref):
    logger.debug('Retrieving reporting unit', ru_ref=ru_ref)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/parties/type/B/ref/{ru_ref}'
    response = requests.get(url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Failed to retrieve reporting unit', ru_ref=ru_ref)
        raise ApiError(response)

    logger.debug('Successfully retrieved reporting unit', ru_ref=ru_ref)
    return response.json()


def get_business_by_party_id(business_party_id, collection_exercise_id=None):
    logger.debug('Retrieving business party',
                 business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/businesses/id/{business_party_id}'
    params = {"collection_exercise_id": collection_exercise_id, "verbose": True}
    response = requests.get(url, params=params, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error retrieving business party',
                  business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved business party',
                 business_party_id=business_party_id, collection_exercise_id=collection_exercise_id)
    return response.json()


def get_respondent_by_party_id(respondent_party_id):
    logger.debug('Retrieving respondent party', respondent_party_id=respondent_party_id)
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/id/{respondent_party_id}'
    response = requests.get(url, auth=app.config['PARTY_AUTH'])

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        log_level = logger.warning if response.status_code in (400, 404) else logger.exception
        log_level('Error retrieving respondent party', respondent_party_id=respondent_party_id)
        raise ApiError(response)

    logger.debug('Successfully retrieved respondent party', respondent_party_id=respondent_party_id)
    return response.json()


def survey_ids_for_respondent(respondent, ru_ref):
    enrolments = [association.get('enrolments')
                  for association in respondent.get('associations')
                  if association['sampleUnitRef'] == ru_ref][0]
    return [enrolment.get('surveyId') for enrolment in enrolments]


def add_enrolment_status_to_respondent(respondent, ru_ref, survey_id):
    association = next((association
                        for association in respondent.get('associations')
                        if association['sampleUnitRef'] == ru_ref), None)
    enrolment_status = next((enrolment['enrolmentStatus']
                             for enrolment in association.get('enrolments')
                             if enrolment['surveyId'] == survey_id), None)
    return {**respondent, 'enrolmentStatus': enrolment_status}


def get_respondent_enrolments(respondent, enrolment_status=None):

    enrolments = []
    for association in respondent['associations']:
        business_party = get_business_by_party_id(association['partyId'])
        for enrolment in association['enrolments']:
            enrolment_data = {
                "business": business_party,
                "survey": get_survey_by_id(enrolment['surveyId']),
                "status": enrolment['enrolmentStatus']
            }
            if enrolment_status:
                if enrolment_data['status'] == enrolment_status:
                    enrolments.append(enrolment_data)
            else:
                enrolments.append(enrolment_data)

    return enrolments


def search_respondent_by_email(email):
    logger.debug('Search respondent via email')

    request_json = {
        'email': email
    }
    url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/email'
    response = requests.get(url, json=request_json, auth=app.config['PARTY_AUTH'])

    if response.status_code == 404:
        return

    try:
        response.raise_for_status()
    except (HTTPError, RequestException):
        log_level = logger.warning if response.status_code is 400 else logger.exception
        log_level("Respondent retrieval failed")
        raise ApiError(response)
    logger.debug("Respondent retrieved successfully")

    return response.json()


def search_respondents(first_name, last_name, email_address, page=0):
    logger.debug('Search respondent by partial match of one or many of first name, last name, and email')

    # TODO: Code to query new party endpoint

    faked_output = [
        {
            'first_name': 'Ivory',
            'last_name': 'Tennant',
            'email': 'itennant0@huffingtonpost.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Ludovika',
            'last_name': 'Bullus',
            'email': 'lbullus1@reddit.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Davis',
            'last_name': 'Burnage',
            'email': 'dburnage2@nih.gov',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Aleen',
            'last_name': 'Heustace',
            'email': 'aheustace3@time.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Emmaline',
            'last_name': 'Bertelet',
            'email': 'ebertelet4@go.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Alexa',
            'last_name': 'Thibodeaux',
            'email': 'athibodeaux5@discovery.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Lay',
            'last_name': 'Aylwin',
            'email': 'laylwin6@unc.edu',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Ryon',
            'last_name': 'Ashfold',
            'email': 'rashfold7@java.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Jeannie',
            'last_name': 'Roger',
            'email': 'jroger8@dell.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Anabelle',
            'last_name': 'Keer',
            'email': 'akeer9@purevolume.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Dorise',
            'last_name': 'Gilleson',
            'email': 'dgillesona@mayoclinic.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Beryl',
            'last_name': 'Van Halle',
            'email': 'bvanhalleb@hibu.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Miner',
            'last_name': 'Willgoss',
            'email': 'mwillgossc@mayoclinic.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Corina',
            'last_name': 'Davenell',
            'email': 'cdavenelld@geocities.jp',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Feodor',
            'last_name': 'Nix',
            'email': 'fnixe@bizjournals.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Deeyn',
            'last_name': 'MacAlroy',
            'email': 'dmacalroyf@ifeng.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Liliane',
            'last_name': 'Birkmyre',
            'email': 'lbirkmyreg@wp.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Hilario',
            'last_name': 'Petken',
            'email': 'hpetkenh@usatoday.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Gavin',
            'last_name': 'Dunham',
            'email': 'gdunhami@sphinn.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Cristionna',
            'last_name': 'McNellis',
            'email': 'cmcnellisj@va.gov',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Carlita',
            'last_name': 'Gilluley',
            'email': 'cgilluleyk@people.com.cn',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Jimmie',
            'last_name': 'Gajewski',
            'email': 'jgajewskil@forbes.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Perri',
            'last_name': 'Berr',
            'email': 'pberrm@samsung.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Garold',
            'last_name': 'Imason',
            'email': 'gimasonn@reddit.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Regan',
            'last_name': 'Riccard',
            'email': 'rriccardo@ustream.tv',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Ilyse',
            'last_name': 'Richt',
            'email': 'irichtp@51.la',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Magda',
            'last_name': 'Zorn',
            'email': 'mzornq@mysql.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Jessalyn',
            'last_name': 'Bollini',
            'email': 'jbollinir@godaddy.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Anjanette',
            'last_name': 'Pitone',
            'email': 'apitones@fda.gov',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Suzanna',
            'last_name': 'Checklin',
            'email': 'schecklint@nydailynews.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Lynsey',
            'last_name': 'Heinz',
            'email': 'lheinzu@flickr.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Travis',
            'last_name': 'Garrettson',
            'email': 'tgarrettsonv@discuz.net',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Ruthann',
            'last_name': 'Agglione',
            'email': 'ragglionew@sourceforge.net',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Wren',
            'last_name': 'Cabell',
            'email': 'wcabellx@vkontakte.ru',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Barn',
            'last_name': 'McCoish',
            'email': 'bmccoishy@mozilla.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Nettie',
            'last_name': 'Sheldrake',
            'email': 'nsheldrakez@usgs.gov',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Savina',
            'last_name': 'Stark',
            'email': 'sstark10@woothemes.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Tucker',
            'last_name': 'Hartland',
            'email': 'thartland11@va.gov',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Raddie',
            'last_name': 'Johananov',
            'email': 'rjohananov12@abc.net.au',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Kerstin',
            'last_name': 'Drover',
            'email': 'kdrover13@thetimes.co.uk',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Elden',
            'last_name': 'Heintsch',
            'email': 'eheintsch14@slashdot.org',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Thom',
            'last_name': 'Cartin',
            'email': 'tcartin15@t.co',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Jinny',
            'last_name': 'Cowen',
            'email': 'jcowen16@nih.gov',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Rozanne',
            'last_name': 'Handscombe',
            'email': 'rhandscombe17@redcross.org',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Willetta',
            'last_name': 'Hendren',
            'email': 'whendren18@google.pl',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Brandy',
            'last_name': 'Habert',
            'email': 'bhabert19@army.mil',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Karly',
            'last_name': 'Klisch',
            'email': 'kklisch1a@networkadvertising.org',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Gaby',
            'last_name': 'Roback',
            'email': 'groback1b@prlog.org',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Desmond',
            'last_name': 'Pallant',
            'email': 'dpallant1c@pagesperso-orange.fr',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Frankie',
            'last_name': 'Lepard',
            'email': 'flepard1d@vimeo.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Phylys',
            'last_name': 'Mildenhall',
            'email': 'pmildenhall1e@usatoday.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Washington',
            'last_name': 'Dyball',
            'email': 'wdyball1f@webnode.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Wenona',
            'last_name': 'Mallam',
            'email': 'wmallam1g@oaic.gov.au',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Philis',
            'last_name': 'Eede',
            'email': 'peede1h@fema.gov',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Cooper',
            'last_name': 'Bentson',
            'email': 'cbentson1i@unc.edu',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Maggee',
            'last_name': 'Mearns',
            'email': 'mmearns1j@multiply.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Vera',
            'last_name': 'Beaver',
            'email': 'vbeaver1k@intel.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Jayson',
            'last_name': 'Haliday',
            'email': 'jhaliday1l@cmu.edu',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Arly',
            'last_name': 'Bottoms',
            'email': 'abottoms1m@cargocollective.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Van',
            'last_name': 'Allsepp',
            'email': 'vallsepp1n@princeton.edu',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Dick',
            'last_name': 'Coie',
            'email': 'dcoie1o@icio.us',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Sherman',
            'last_name': 'Whittle',
            'email': 'swhittle1p@marketwatch.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Noelani',
            'last_name': 'Finnick',
            'email': 'nfinnick1q@weebly.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Vito',
            'last_name': 'Camosso',
            'email': 'vcamosso1r@nifty.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Morlee',
            'last_name': 'Connal',
            'email': 'mconnal1s@github.io',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Quinn',
            'last_name': 'Grayley',
            'email': 'qgrayley1t@miitbeian.gov.cn',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Mildrid',
            'last_name': 'Baggelley',
            'email': 'mbaggelley1u@bbb.org',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Son',
            'last_name': 'D\'Onise',
            'email': 'sdonise1v@ezinearticles.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Sallyanne',
            'last_name': 'Pagram',
            'email': 'spagram1w@mozilla.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Johannes',
            'last_name': 'Cryer',
            'email': 'jcryer1x@facebook.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Claretta',
            'last_name': 'Goodboddy',
            'email': 'cgoodboddy1y@nature.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Doris',
            'last_name': 'Maxworthy',
            'email': 'dmaxworthy1z@people.com.cn',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Debra',
            'last_name': 'Dempster',
            'email': 'ddempster20@dropbox.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Duncan',
            'last_name': 'Puckinghorne',
            'email': 'dpuckinghorne21@technorati.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Leroy',
            'last_name': 'Witcomb',
            'email': 'lwitcomb22@spotify.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Donni',
            'last_name': 'Verbeek',
            'email': 'dverbeek23@examiner.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Rosemarie',
            'last_name': 'Capinetti',
            'email': 'rcapinetti24@nationalgeographic.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Laverne',
            'last_name': 'Leppingwell',
            'email': 'lleppingwell25@theatlantic.com',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Randy',
            'last_name': 'Izkovitch',
            'email': 'rizkovitch26@netvibes.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Eleonora',
            'last_name': 'Tomaszynski',
            'email': 'etomaszynski27@epa.gov',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Austen',
            'last_name': 'Kerbler',
            'email': 'akerbler28@umich.edu',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Reuben',
            'last_name': 'Lambert-Ciorwyn',
            'email': 'rlambertciorwyn29@tamu.edu',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Sumner',
            'last_name': 'Grout',
            'email': 'sgrout2a@desdev.cn',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Leeanne',
            'last_name': 'Rosario',
            'email': 'lrosario2b@reference.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Matelda',
            'last_name': 'Lopez',
            'email': 'mlopez2c@examiner.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Cathleen',
            'last_name': 'Poe',
            'email': 'cpoe2d@yale.edu',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Krystle',
            'last_name': 'Donwell',
            'email': 'kdonwell2e@mayoclinic.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Mala',
            'last_name': 'Isham',
            'email': 'misham2f@nydailynews.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Sallee',
            'last_name': 'Bricksey',
            'email': 'sbricksey2g@exblog.jp',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Eberhard',
            'last_name': 'Featley',
            'email': 'efeatley2h@rakuten.co.jp',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Fraze',
            'last_name': 'MacBrearty',
            'email': 'fmacbrearty2i@smh.com.au',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Aloysia',
            'last_name': 'Lendrem',
            'email': 'alendrem2j@taobao.com',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Hakim',
            'last_name': 'Forton',
            'email': 'hforton2k@ucoz.ru',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Norman',
            'last_name': 'Dudney',
            'email': 'ndudney2l@ucoz.ru',
            'state': 'ACTIVE'
        },
        {
            'first_name': 'Ron',
            'last_name': 'Dederich',
            'email': 'rdederich2m@nbcnews.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Alvis',
            'last_name': 'Americi',
            'email': 'aamerici2n@nymag.com',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Bobbye',
            'last_name': 'Ivshin',
            'email': 'bivshin2o@is.gd',
            'state': 'INACTIVE'
        },
        {
            'first_name': 'Damiano',
            'last_name': 'Grasner',
            'email': 'dgrasner2p@virginia.edu',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Essy',
            'last_name': 'Eva',
            'email': 'eeva2q@archive.org',
            'state': 'SUSPENDED'
        },
        {
            'first_name': 'Gerhard',
            'last_name': 'Moncreiffe',
            'email': 'gmoncreiffe2r@nhs.uk',
            'state': 'SUSPENDED'
        }
    ]

    return faked_output


def update_contact_details(ru_ref, respondent_id, form):
    logger.debug('Updating respondent details', respondent_id=respondent_id)

    new_contact_details = {
        "firstName": form.get('first_name'),
        "lastName": form.get('last_name'),
        "email_address": form.get('hidden_email'),
        "new_email_address": form.get('email'),
        "telephone": form.get('telephone')
    }

    old_contact_details = get_respondent_by_party_id(respondent_id)
    contact_details_changed = _compare_contact_details(new_contact_details, old_contact_details)

    if len(contact_details_changed) > 0:
        url = f'{app.config["PARTY_URL"]}/party-api/v1/respondents/id/{respondent_id}'
        response = requests.put(url, json=new_contact_details, auth=app.config['PARTY_AUTH'])

        if response.status_code != 200:
            raise UpdateContactDetailsException(ru_ref, EditContactDetailsForm(form),
                                                old_contact_details, response.status_code)

        logger.debug('Respondent details updated', respondent_id=respondent_id, status_code=response.status_code)

    return contact_details_changed


def _compare_contact_details(new_contact_details, old_contact_details):
    # Currently the 'get contact details' and 'update respondent details' keys do not match and must be mapped
    contact_details_map = {
        "firstName": "firstName",
        "lastName": "lastName",
        "telephone": "telephone",
        "emailAddress": "new_email_address"}

    return {old_key for old_key, new_key in contact_details_map.items()
            if old_contact_details[old_key] != new_contact_details[new_key]}
