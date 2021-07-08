import json


def test_load_gdc_data():
    """
    Load the GDC JSON data.
    """
    with open('head-and-mouth/gdc-head-and-mouth.json') as file:
        gdc_head_and_mouth = json.load(file)

    assert len(gdc_head_and_mouth) > 0, "At least one GDC Head and Mouth case loaded."

    