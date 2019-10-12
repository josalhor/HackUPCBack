from typing import Dict, List

field_to_preference_mapping = {
    'pTJg7wyEVVG8': ('email', 'email'),
    'I8nCSM4LmSzm': ('adults', 'number'),
    'pvTvCy1mihaN': ('children', 'number'),
    'CC1jhfNy43XU': ('why', 'choice'),
    'G9bqBcmNiCub': ('city', 'text'),
    'IauIBJ5QQCq6': ('square_meters', 'choice'),
    'sgfZG0zYXqy7': ('rental_or_buying', 'choice'),
    'tCaBtzD1T8xW': ('schools', 'number'),
    'OIR5viLC9MdX': ('pharmacies', 'number'),
    'UOp5vdYdS8rn': ('hospitals', 'number'),
    'wd1DcQANxD3h': ('bedrooms', 'number'),
    'YzkKhQ1cdy6g': ('bathrooms', 'number'),
}


def parse_answers(answers: List) -> Dict[str, str]:
    answers_parsed = dict()
    for answer in answers:
        field_id = answer['event_id']
        field_name, field_type = field_to_preference_mapping[field_id]
        if field_type is 'choice':
            value = answer[field_type]['label']
        else:
            value = answer[field_type]

        answers_parsed[field_name] = value

    return answers_parsed
