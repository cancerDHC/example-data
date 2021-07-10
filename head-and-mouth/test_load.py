import json
import pytest

import ccdhmodel as ccdh
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml_runtime.dumpers.json_dumper import JSONDumper

def create_body_site(site_name):
    """ Create a CCDH BodySite based on the name of a site in the human body."""

    # Accept 'None'.
    if site_name is None:
        return None

    # Some body sites are not currently included in the CCDH model. We will need to translate these sites
    # into values that *are* included in the CCDH model.
    site_mappings = {
        'Larynx, NOS': ccdh.EnumCCDHBodySiteSite.Larynx
    }

    # Map values if needed. Otherwise, pass them through unmapped.
    if site_name in site_mappings:
        return ccdh.BodySite(site=(site_mappings[site_name]))

    return ccdh.BodySite(site=site_name)


def test_create_body_site():
    with pytest.raises(ValueError):
        create_body_site('Laryn')

    body_site_larynx = create_body_site('Larynx')
    body_site_larynx_nos = create_body_site('Larynx, NOS')

    assert type(body_site_larynx) is ccdh.BodySite
    assert body_site_larynx.site.code.text == ccdh.EnumCCDHBodySiteSite.Larynx.text

    assert type(body_site_larynx_nos) is ccdh.BodySite
    assert body_site_larynx_nos.site.code.text == ccdh.EnumCCDHBodySiteSite.Larynx.text


def create_stage_observation(type, value):
    """ Create a CCDHCancerStageObservation from a type of observation and a codeable concept."""
    # As with the body site example above, we need to map GDC values into the values
    # allowed under the CCDH model.
    stage_mappings = {
        'not reported': 'Not Reported',
        'unknown': 'Unknown',
        'stage i': 'Stage I',
        'stage ii': 'Stage II',
        'stage iii': 'Stage III',
        'stage iva': 'Stage IVA',
        'stage ivb': 'Stage IVB',
        'stage ivc': 'Stage IVC',
    }

    if value in stage_mappings:
        return ccdh.CancerStageObservation(
            observation_type=type,
            valueCodeableConcept=stage_mappings[value]
        )

    return ccdh.CancerStageObservation(
        observation_type=type,
        valueCodeableConcept=value
    )


def test_create_stage_observation():
    obs1 = create_stage_observation('Pathological Node (N)', 'Stage III')
    assert type(obs1) is ccdh.CancerStageObservation
    assert obs1.observation_type.code.text == 'Pathological Node (N)'
    assert obs1.valueCodeableConcept.code.text == 'Stage III'

    # Both observation type and valueCodeableConcept are enumerations.
    with pytest.raises(ValueError):
        create_stage_observation('Pathological Node', 'Stage III')

    with pytest.raises(ValueError):
        create_stage_observation('Pathological Node (N)', 'Stage XI')


def create_stage_from_gdc(diagnosis):
    cancer_stage_method_type = None
    if diagnosis.get('ajcc_staging_system_edition') == '7th':
        cancer_stage_method_type = 'AJCC staging system 7th edition'

    # Create an observation set
    obs = ccdh.CancerStageObservationSet(
        method_type=cancer_stage_method_type
    )

    # Add observations for every type of observation in the GDC diagnosis.
    if diagnosis.get('tumor_stage') is not None:
        obs.observations.append(create_stage_observation('Overall', diagnosis.get('tumor_stage')))

    if diagnosis.get('ajcc_clinical_stage') is not None:
        obs.observations.append(create_stage_observation('Clinical Overall', diagnosis.get('ajcc_clinical_stage')))

    if diagnosis.get('ajcc_clinical_t') is not None:
        obs.observations.append(create_stage_observation('Clinical Tumor (T)', diagnosis.get('ajcc_clinical_t')))

    if diagnosis.get('ajcc_clinical_n') is not None:
        obs.observations.append(create_stage_observation('Clinical Node (N)', diagnosis.get('ajcc_clinical_n')))

    if diagnosis.get('ajcc_clinical_m') is not None:
        obs.observations.append(create_stage_observation('Clinical Metastasis (M)', diagnosis.get('ajcc_clinical_m')))

    if diagnosis.get('ajcc_pathologic_stage') is not None:
        obs.observations.append(
            create_stage_observation('Pathological Overall', diagnosis.get('ajcc_pathologic_stage')))

    if diagnosis.get('ajcc_pathologic_t') is not None:
        obs.observations.append(create_stage_observation('Pathological Tumor (T)', diagnosis.get('ajcc_pathologic_t')))

    if diagnosis.get('ajcc_pathologic_n') is not None:
        obs.observations.append(create_stage_observation('Pathological Node (N)', diagnosis.get('ajcc_pathologic_n')))

    if diagnosis.get('ajcc_pathologic_m') is not None:
        obs.observations.append(
            create_stage_observation('Pathological Metastasis (M)', diagnosis.get('ajcc_pathologic_m')))

    return obs


def test_create_stage_from_gdc():
    diag1 = {
        'ajcc_staging_system_edition': '7th',
        'ajcc_pathologic_stage': 'Stage III'
    }
    stage = create_stage_from_gdc(diag1)
    assert type(stage) is ccdh.CancerStageObservationSet

def transform_sample_to_specimen(sample):
    """
    A method for transforming a GDC Sample into CCDH Specimen.
    """
    specimen = ccdh.Specimen(id=sample.get('sample_id'))
    specimen.source_material_type = sample.get('sample_type')
    specimen.general_tissue_morphology = sample.get('tissue_type')
    specimen.specific_tissue_morphology = sample.get('tumor_code')
    specimen.tumor_status_at_collection = sample.get('tumor_descriptor')
    specimen.creation_activity = ccdh.SpecimenCreationActivity(
        date_ended=ccdh.TimePoint(
            dateTime=sample.get('created_datetime')
        )
    )
    return specimen


def transform_diagnosis(diagnosis, case):
    ccdh_diagnosis = ccdh.Diagnosis(
        id=diagnosis.get('diagnosis_id'),
        condition=diagnosis.get('primary_diagnosis'),
        morphology=diagnosis.get('morphology'),
        metastatic_site=create_body_site(diagnosis.get('primary_site')),
        grade=diagnosis.get('grade'),
        stage=create_stage_from_gdc(diagnosis),
        year_at_diagnosis=diagnosis.get('year_of_diagnosis'),
        related_specimen=[
            transform_sample_to_specimen(
                sample
            ) for sample in case.get('samples')
        ]
    )
    ccdh_diagnosis.identifier = [
        ccdh.Identifier(
            system='GDC-submitter-id',
            value=diagnosis.get('submitter_id')
        )
    ]

    return ccdh_diagnosis


def test_transform_gdc_data():
    """
    Transform the GDC JSON data into JSON-LD.
    """
    with open('head-and-mouth/gdc-head-and-mouth.json') as file:
        gdc_head_and_mouth = json.load(file)

    assert len(gdc_head_and_mouth) > 0, "At least one GDC Head and Mouth case loaded."

    jsonldContext = ContextGenerator('ccdh/ccdhmodel.yaml').serialize()
    jsonldContextAsDict = json.loads(jsonldContext)
    assert type(jsonldContextAsDict) is dict

    diag1_as_jsonld = JSONDumper.dump(
        transform_diagnosis(
            gdc_head_and_mouth[131]['diagnoses'][0],
            gdc_head_and_mouth[131]
        ), jsonldContext)
    assert diag1_as_jsonld is str
    diag1 = json.loads(diag1_as_jsonld)
    assert type(diag1) is dict
