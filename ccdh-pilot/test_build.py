# This file tests whether we can generate demonstrator data using the Python data classes.

import crdch_model
from linkml_runtime.dumpers import yaml_dumper

def test_d1_gdc_specimen_create():
    specimen = crdch_model.Specimen(id='f2f:05f1574e-2a28-50bc-bdc1-e4c6dee92fd1')
    specimen.identifier.append({
        'value': 'target:TARGET-40-0A4I9I-01A'
    })
    specimen.identifier.append({
        'value': 'gdc-sample:9575763d-9c34-4e8e-a43a-419f5c13962f'
    })
    specimen.identifier.append({
        'value': 'biosample: SAMEA1652204'
    })
    assert yaml_dumper.dumps(specimen) != ''
