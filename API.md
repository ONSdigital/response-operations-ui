# response operations ui routes

This page documents the response operations ui endpoints that can be hit.

## Response Status Endpoints

`case/<ru_ref>/response-status`
* GET request to this endpoint allows you to get the response status.
* POST request to this endpoint allows you to update the response status.
* `ru_ref` is the reference of the response status.

## Collection Exercise Endpoints

`surveys/<short_name>/<period>`
* GET request to this endpoint allows you to view the collection exercise.
* POST request to this endpoint allows you to post the collection exercise.
* `short_name` is the abbreviated name of the collection exercise.
* `period` is the time period of the collection exercise.

`surveys/response_chasing/<ce_id>/<survey_id>`
* GET request to this endpoint handles formatting/uploading/selecting/deselecting collection instruments and samples.
* `ce_id` is the collection exercise ID.
* `survey_id` is the survey ID.

`surveys/<short_name>/<period>/edit-collection-exercise-period-id`
* GET request to this endpoint allows you to view collection exercise details.
* POST request to this endpoint allows you to view editing collection exercise details.
* `short_name` is the abbreviated name of the collection exercise.
* `period` is the time period of the collection exercise.

`surveys/<survey_ref>/<short_name>/create-collection-exercise`
* GET request to this endpoint allows you to get the collection exercise creation form.
* POST request to this endpoint allows you to create the collection exercise.
* `survey_ref` is the reference of the survey.
* `short_name` is the abbreviated name of the collection exercise.

`surveys/<short_name>/<period>/<ce_id>/confirm-create-event/<tag>`
* GET request to this endpoint allows you to get the collection exercise event creation form.
* POST request to this endpoint allows you to create a collection exercise event.
* `short_name` is the abbreviated name of the collection exercise.
* `period` is the time period of the collection exercise.
* `ce_id` is the collection exercise ID.
* `tag` is the event name tag.

`surveys/<short_name>/<period>/confirm-remove-sample`
* GET request to this endpoint confirms removing a sample.
* POST request to this endpoint removes a loaded sample.
* `short_name` is the abbreviated name of the collection exercise.
* `period` is the time period of the collection exercise.

## Home Endpoints

`/home`
* GET request to this endpoint allows you to access the homepage.

## Info Endpoints

`/info`
* GET request to this endpoint displays the info of the response operations ui.

## Logout Endpoints

`/logout`
* GET request to this endpoint signs the user out.

## Message Endpoints

`messages`
* GET request to this endpoint allows you to view the selected survey.

`messages/create-message`
* POST request to this endpoint allows you to create a message.

`messages/threads/<thread_id>`
* GET request to this endpoint allows you to view a message conversation.
* POST request to this endpoint allows you to re-open a previously closed conversation.

`messages/mark_unread/<message_id>`
* GET request to this endpoint allows you to mark a message as unread.
* `message_id` is the ID of the message.

`messages/select-inbox`
* GET and POST requests to this endpoint allow you to select which inbox to view.

`messages/<selected-survey>`
* GET request to this endpoint allows you to view the selected survey.
* `selected-survey` is the name of the selected survey.

`messages/threads/<thread_id>/close-conversation`
* GET and POST requests to this endpoint allow you to close a conversation.
* `thread_id` is the ID of the conversation thread.

## Reporting Units Endpoints

`reporting-units/<ru_ref>`
* GET request to this endpoint allows you to view a reporting unit.
* `ru_ref` is the reference of the reporting unit.

`reporting-units/<ru_ref>/edit-contact-details/<respondent_id>`
* GET request to this endpoint allows you to view the contact details of a respondent.
* POST request to this endpoint allows you to edit the contact details of a respondent.
* `ru_ref` is the reference of the reporting unit.
* `respondent_id` is the ID of the respondent.

`reporting-units`
* GET and POST requests to this endpoint search for reporting units.

`reporting-units/resend_verification/<ru_ref>/<party_id>`
* GET request to this endpoint allows you view the re-sent verification e-mail.
* POST request to this endpoint allows you to re-send the verification e-mail.
* `ru_ref` is the reference of the reporting unit.
* `party_id` is the ID of the party.

`reporting-units/<ru_ref>/new_enrolment_code`
* GET request to this endpoint generates a new enrolment code.
* `ru_ref` is the reference of the reporting unit.

`reporting-units/<ru_ref>/change-enrolment-status`
* GET request to this endpoint confirms the change to the enrolment status.
* POST request to this endpoint changes th enrolment status.
* `ru_ref` is the reference of the reporting unit.

`reporting-units/<ru_ref>/change-respondent-status`
* GET request to this endpoint confirms the change to the respondent status.
* POST request to this endpoint changes the respondent status.
* `ru_ref` is the reference of the reporting unit.

## Respondent Endpoints

`respondents`
* GET request to this endpoint loads the respondent search home.

`respondents/search`
* POST request to this endpoint redirects the respondent search form.
* GET request to this endpoint shows the results of the respondent search.

`respondents/respondent-details/<respondent_id>`
* GET request to this endpoint shows the respondent details.
* `respondent_id` is the ID of the respondent.

`respondents/edit-contact-details/<respondent_id>`
* GET request to this endpoint allows you to view the contact details of a respondent.
* POST request to this endpoint allows you to edit the contact details of a respondent.
* `respondent_id` is the ID of the respondent.

`respondents/resend_verification/<respondent_id>`
* GET request to this endpoint allows you to view the re-sent verification e-mail.
* `respondent_id` is the ID of the respondent.

`respondents/resend_verification/<party_id>`
* POST request to this endpoint allows you to resend the verification e-mail.
* `party_id` is the ID of the party.

`respondents/<respondent_id>/change-enrolment-status`
* POST request to this endpoint allows you to change the enrolment status of a respondent.
* `respondent_id` is the ID of the respondent.

`respondents/<respondent_id>/change-respondent-status`
* POST request to this endpoint allows you to change the respondent status of a respondent.
* `respondent_id` is the ID of the respondent.

`respondents/<party_id>/change-respondent-status`
* GET request to this endpoint allows you to confirm the change to a respondent's status.
* `party_id` is the ID of the party.

## Sign-in Endpoints

`/sign-in`
* GET and POST requests to this endpoints allows you to sign in.

## Survey Endpoints

`surveys`
* GET request to this endpoint allows you to view the list of surveys.

`surveys/<short_name>`
* GET request to this endpoint allows you to find a specific survey.
* `short_name` is the abbreviated name of the collection exercise.

`surveys/edit-survey-details/<short_name>`
* GET request to this endpoint allows you to view the details of a survey.
* POST request to this endpoint allows you to edit the details of a survey.
* `short_name` is the abbreviated name of the collection exercise.

`surveys/create`
* GET request to this endpoint displays the survey creation form.
* POST request to this endpoint allows you to create a survey.

`/<short_name>/<period>/event/<tag>`
* GET request to this endpoint allows you to update an event date.
* POST request to this endpoint allows you to submit the updated event date.
* `short_name` is the abbreviated name of the collection exercise.
* `period` is the time period of the collection exercise.
* `tag` is the event name tag.
