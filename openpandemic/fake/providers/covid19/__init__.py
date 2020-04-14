# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

from typing import List, Dict, Tuple
from faker.providers import BaseProvider


localized = True


class Provider(BaseProvider):
    """Provider for Faker which adds fake COVID-19 evaluations."""

    questions_score = {
        "mas_20_dias": -15,
        "tos": 15,
        "fiebre": 15,
        "contacto_positivo": 29,
        "gastrointestinal": 0,
        "mucosidad": 0,
        "falta_aire": 60,
        "dolor_muscular": 0,
        "covid19_curado": 0
    }

    def covid19_questions_result(self, threshold: int = 30) -> Tuple[List[Dict], str]:
        """
        Return an evaluation question and its result
        :param threshold: threshold value to mark an evaluation as 'symptom', 'no-symptom' in other case
        :return: evaluation questions and its result
        """

        questions_fake_values = tuple(self.random_int(0, 1) for _ in self.questions_score.values())

        score = sum([x * y for x, y in zip(questions_fake_values, self.questions_score.values())])

        result_test = 'symptoms' if score >= threshold else 'no-symptoms'

        questions_kv_int = dict(zip(self.questions_score.keys(), questions_fake_values))

        questions_kv = [dict(KEY=k, VALUE="true" if v == 1 else "false") for (k, v) in questions_kv_int.items()]

        return questions_kv, result_test
