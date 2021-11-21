import pandas as pd
from django.db import transaction
from string_grouper import group_similar_strings
from mainapp.models import Subject


def update_subjects():
    print("update_subjects")

    subjects = Subject.objects.all()

    subjects_url_unsuffixed = [(subject.url_name, subject.url_name.rsplit('_(')[0]) for subject in subjects]
    subjects_pd = pd.DataFrame(subjects_url_unsuffixed, columns=['id', 'unsuffixed'])

    subjects_pd[['group_name']] = group_similar_strings(subjects_pd['unsuffixed'],
                                                        min_similarity=0.85, ignore_index=True)

    subject_url_norm = {url: normalized for url, _, normalized in subjects_pd.values.tolist()}

    with transaction.atomic():
        for subject in subjects:
            subject.name_normalized = subject_url_norm[subject.url_name]
            subject.save()
