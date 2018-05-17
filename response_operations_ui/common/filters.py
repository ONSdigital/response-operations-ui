def get_collection_exercise_by_period(exercises, period):
    for exercise in exercises:
        if exercise['exerciseRef'] == period:
            return exercise


def get_case_group_status_by_collection_exercise(case_groups, collection_exercise_id):
    for case_group in case_groups:
        if case_group['collectionExerciseId'] == collection_exercise_id:
            return case_group['caseGroupStatus']
