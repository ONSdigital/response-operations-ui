import datetime
import logging

import requests
from structlog import wrap_logger

from response_operations_ui import app
from response_operations_ui.exceptions.exceptions import ApiError

logger = wrap_logger(logging.getLogger(__name__))


def upload_sample(ce_id, file, total_businesses, total_ci):
    logger.debug('Uploading sample', collection_exercise_id=ce_id)
    url = f'{app.config["BACKSTAGE_API_URL"]}/sample/upload/{ce_id}'
    response = requests.post(url, files={"file": (file.filename, file.stream, file.mimetype)})
    if response.status_code != 201:
        raise ApiError(response)

    logger.debug('Successfully uploaded sample',
                 collection_exercise_id=ce_id,
                 filename=file.filename)

    return sample_summary(total_businesses, total_ci)


def sample_summary(total_businesses, total_ci):
        sample = {"businesses": total_businesses,
                  "collection_instruments": total_ci,
                  "submission_time": datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
                  }

        return sample
