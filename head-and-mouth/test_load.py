import sys
import os
import json
import pytest
import logging
import rdflib

from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml_runtime.dumpers import json_dumper

import crdch_model as ccdh

# The URI where the CRDCH YAML file is located.
CRDCH_YAML_URI = 'https://raw.githubusercontent.com/cancerDHC/ccdhmodel/v1.1/model/schema/crdch_model.yaml'

def codeable_concept(text, system, code):
    if code is None:
        return None

    return ccdh.CodeableConcept(
        text=text,
        coding=ccdh.Coding(
            system=system,
            code=code
        )
    )

def create_body_site(site_name):
    """ Create a CCDH BodySite based on the name of a site in the human body."""

    # Accept 'None'.
    if site_name is None:
        return None

    # Some body sites are not currently included in the CCDH model. We will need to translate these sites
    # into values that *are* included in the CCDH model.
    site_mappings = {
        'Larynx, NOS': ccdh.EnumCRDCHBodySiteSite.Larynx.text
    }

    # Map values if needed. Otherwise, pass them through unmapped.
    if site_name in site_mappings:
        return ccdh.BodySite(site=codeable_concept(site_name, 'GDC', site_mappings[site_name]))

    return ccdh.BodySite(site=codeable_concept(site_name, 'GDC', site_name))


def test_create_body_site():
    #with pytest.raises(ValueError):
    #    create_body_site('Laryn')

    body_site_larynx = create_body_site('Larynx')
    body_site_larynx_nos = create_body_site('Larynx, NOS')

    assert type(body_site_larynx) is ccdh.BodySite
    assert body_site_larynx.site.coding[0].code == ccdh.EnumCRDCHBodySiteSite.Larynx.text

    assert type(body_site_larynx_nos) is ccdh.BodySite
    assert body_site_larynx_nos.site.coding[0].code == ccdh.EnumCRDCHBodySiteSite.Larynx.text


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
            observation_type=codeable_concept(type, 'GDC', type),
            value_codeable_concept=codeable_concept(value, 'GDC', stage_mappings[value])
        )

    return ccdh.CancerStageObservation(
        observation_type=codeable_concept(type, 'GDC', type),
        value_codeable_concept=codeable_concept(value, 'GDC', value)
    )


def test_create_stage_observation():
    obs1 = create_stage_observation('Pathological Node (N)', 'Stage III')
    assert type(obs1) is ccdh.CancerStageObservation
    assert obs1.observation_type.coding[0].code == 'Pathological Node (N)'
    assert obs1.value_codeable_concept.coding[0].code == 'Stage III'

    # Both observation type and value_codeable_concept are enumerations.
    #with pytest.raises(ValueError):
    #    create_stage_observation('Pathological Node', 'Stage III')

    #with pytest.raises(ValueError):
    #    create_stage_observation('Pathological Node (N)', 'Stage XI')


def create_stage_from_gdc(diagnosis):
    cancer_stage_method_type = None
    if diagnosis.get('ajcc_staging_system_edition') == '7th':
        cancer_stage_method_type = codeable_concept('7th', 'GDC', 'AJCC staging system 7th edition')

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
    specimen.source_material_type = codeable_concept(sample.get('sample_type'), 'GDC', sample.get('sample_type'))
    specimen.general_tissue_morphology = codeable_concept(sample.get('tissue_type'), 'GDC', sample.get('tissue_type'))
    specimen.specific_tissue_morphology = codeable_concept(sample.get('tumor_code'), 'GDC', sample.get('tumor_code'))
    specimen.tumor_status_at_collection = codeable_concept(sample.get('tumor_descriptor'), 'GDC', sample.get('tumor_descriptor'))
    specimen.creation_activity = ccdh.SpecimenCreationActivity(
        date_ended=ccdh.TimePoint(
            date_time=sample.get('created_datetime')
        )
    )
    return specimen


def transform_diagnosis(diagnosis, case):
    samples = list(filter(lambda x: x is not None, map(transform_sample_to_specimen, case.get('samples') or [])))

    ccdh_diagnosis = ccdh.Diagnosis(
        id=diagnosis.get('diagnosis_id'),
        condition=codeable_concept(diagnosis.get('primary_diagnosis'), 'GDC', diagnosis.get('primary_diagnosis')),
        morphology=codeable_concept(diagnosis.get('morphology'), 'GDC', diagnosis.get('morphology')),
        grade=diagnosis.get('grade'),
        stage=create_stage_from_gdc(diagnosis),
        # diagnosis_date=ccdh.TimePoint(date_time=diagnosis.get('year_of_diagnosis')),
        related_specimen=samples,
        identifier=[
            ccdh.Identifier(
                system='GDC-submitter-id',
                value=diagnosis.get('submitter_id')
            )
        ]
    )

    if 'primary_site' in case and case['primary_site'] != '':
        body_site = create_body_site(case['primary_site'])
        if body_site is not None:
            ccdh_diagnosis.metastatic_site.append(body_site)

    return ccdh_diagnosis


def test_transform_diagnosis():
    """
    Test whether we can transform diagnoses into a CCDH Diagnosis object.
    """

    # This is a case from GDC: https://portal.gdc.cancer.gov/cases/422a72e7-fe76-411d-b59e-1f0f0812c3cf
    case1 = {'aliquot_ids': ['96f09bc8-a194-482c-bd17-baf28739e4f8'], 'case_id': '422a72e7-fe76-411d-b59e-1f0f0812c3cf',
             'created_datetime': '2018-09-13T13:42:10.444091-05:00', 'days_to_lost_to_followup': None, 'diagnoses': [
            {'age_at_diagnosis': None, 'ajcc_clinical_m': None, 'ajcc_clinical_n': None, 'ajcc_clinical_stage': None,
             'ajcc_clinical_t': None, 'ajcc_pathologic_m': None, 'ajcc_pathologic_n': None,
             'ajcc_pathologic_stage': None, 'ajcc_pathologic_t': None, 'ajcc_staging_system_edition': None,
             'anaplasia_present': None, 'anaplasia_present_type': None, 'ann_arbor_b_symptoms': None,
             'ann_arbor_clinical_stage': None, 'ann_arbor_extranodal_involvement': None,
             'ann_arbor_pathologic_stage': None, 'best_overall_response': None, 'breslow_thickness': None,
             'burkitt_lymphoma_clinical_variant': None, 'child_pugh_classification': None,
             'circumferential_resection_margin': None, 'classification_of_tumor': None, 'cog_liver_stage': None,
             'cog_neuroblastoma_risk_group': None, 'cog_renal_stage': None, 'cog_rhabdomyosarcoma_risk_group': None,
             'created_datetime': '2018-09-22T00:57:04.451898-05:00', 'days_to_best_overall_response': None,
             'days_to_diagnosis': None, 'days_to_last_follow_up': None, 'days_to_last_known_disease_status': None,
             'days_to_recurrence': None, 'diagnosis_id': '842d6984-7c03-4ab6-95db-42fa2ea699db',
             'enneking_msts_grade': None, 'enneking_msts_metastasis': None, 'enneking_msts_stage': None,
             'enneking_msts_tumor_site': None, 'esophageal_columnar_dysplasia_degree': None,
             'esophageal_columnar_metaplasia_present': None, 'figo_stage': None,
             'first_symptom_prior_to_diagnosis': None, 'gastric_esophageal_junction_involvement': None,
             'gleason_grade_group': None, 'goblet_cells_columnar_mucosa_present': None, 'gross_tumor_weight': None,
             'icd_10_code': None, 'igcccg_stage': None, 'inpc_grade': None, 'inpc_histologic_group': None,
             'inrg_stage': None, 'inss_stage': None, 'international_prognostic_index': None, 'irs_group': None,
             'irs_stage': None, 'ishak_fibrosis_score': None, 'iss_stage': None,
             'largest_extrapelvic_peritoneal_focus': None, 'last_known_disease_status': 'not reported',
             'laterality': None, 'lymph_nodes_positive': None, 'lymph_nodes_tested': None,
             'lymphatic_invasion_present': None, 'masaoka_stage': None,
             'medulloblastoma_molecular_classification': None, 'metastasis_at_diagnosis': None,
             'metastasis_at_diagnosis_site': None, 'method_of_diagnosis': None, 'micropapillary_features': None,
             'mitosis_karyorrhexis_index': None, 'mitotic_count': None, 'morphology': '8070/3',
             'non_nodal_regional_disease': None, 'non_nodal_tumor_deposits': None, 'ovarian_specimen_status': None,
             'ovarian_surface_involvement': None, 'percent_tumor_invasion': None, 'perineural_invasion_present': None,
             'peripancreatic_lymph_nodes_positive': None, 'peripancreatic_lymph_nodes_tested': None,
             'peritoneal_fluid_cytological_status': None, 'primary_diagnosis': 'Squamous cell carcinoma, NOS',
             'primary_gleason_grade': None, 'prior_malignancy': None, 'prior_treatment': None,
             'progression_or_recurrence': 'not reported', 'residual_disease': None, 'secondary_gleason_grade': None,
             'site_of_resection_or_biopsy': 'Larynx, NOS', 'state': 'released',
             'submitter_id': 'GENIE-DFCI-010671-11105_diagnosis', 'supratentorial_localization': None,
             'synchronous_malignancy': None, 'tissue_or_organ_of_origin': 'Larynx, NOS',
             'tumor_confined_to_organ_of_origin': None, 'tumor_focality': None, 'tumor_grade': 'Not Reported',
             'tumor_largest_dimension_diameter': None, 'tumor_regression_grade': None, 'tumor_stage': 'not reported',
             'updated_datetime': '2019-11-18T13:54:59.294543-06:00', 'vascular_invasion_present': None,
             'vascular_invasion_type': None, 'weiss_assessment_score': None, 'wilms_tumor_histologic_subtype': None,
             'year_of_diagnosis': None}], 'diagnosis_ids': ['842d6984-7c03-4ab6-95db-42fa2ea699db'],
             'disease_type': 'Squamous Cell Neoplasms', 'id': '422a72e7-fe76-411d-b59e-1f0f0812c3cf',
             'index_date': 'Initial Genomic Sequencing', 'lost_to_followup': None, 'primary_site': 'Larynx',
             'sample_ids': ['6f9eeaa3-8bd1-479c-a0fc-98317eb458dc'], 'samples': [
            {'biospecimen_anatomic_site': None, 'biospecimen_laterality': None, 'catalog_reference': None,
             'composition': None, 'created_datetime': '2018-09-24T17:56:43.873530-05:00', 'current_weight': None,
             'days_to_collection': None, 'days_to_sample_procurement': None, 'diagnosis_pathologically_confirmed': None,
             'distance_normal_to_tumor': None, 'distributor_reference': None, 'freezing_method': None,
             'growth_rate': None, 'initial_weight': None, 'intermediate_dimension': None, 'is_ffpe': None,
             'longest_dimension': None, 'method_of_sample_procurement': None, 'oct_embedded': None,
             'passage_count': None, 'pathology_report_uuid': None, 'preservation_method': None,
             'sample_id': '6f9eeaa3-8bd1-479c-a0fc-98317eb458dc', 'sample_type': 'Primary Tumor',
             'sample_type_id': None, 'shortest_dimension': None, 'state': 'released',
             'submitter_id': 'GENIE-DFCI-010671-11105', 'time_between_clamping_and_freezing': None,
             'time_between_excision_and_freezing': None, 'tissue_type': 'Not Reported', 'tumor_code': None,
             'tumor_code_id': None, 'tumor_descriptor': None, 'updated_datetime': '2019-11-18T13:54:59.294543-06:00'}],
             'state': 'released', 'submitter_aliquot_ids': ['GENIE-DFCI-010671-11105_aliquot'],
             'submitter_diagnosis_ids': ['GENIE-DFCI-010671-11105_diagnosis'], 'submitter_id': 'GENIE-DFCI-010671',
             'submitter_sample_ids': ['GENIE-DFCI-010671-11105'],
             'updated_datetime': '2019-11-18T13:54:59.294543-06:00'}

    assert case1['primary_site'] == 'Larynx'

    diagnosis = transform_diagnosis(case1['diagnoses'][0], case1)
    assert type(diagnosis) is ccdh.Diagnosis
    assert diagnosis.id == '842d6984-7c03-4ab6-95db-42fa2ea699db'
    assert diagnosis.metastatic_site == [create_body_site('Larynx')]

def test_transform_gdc_data():
    """
    Transform the GDC JSON data into JSON-LD.
    """
    with open('head-and-mouth/gdc-head-and-mouth.json') as file:
        gdc_head_and_mouth = json.load(file)

    assert len(gdc_head_and_mouth) > 0, "At least one GDC Head and Mouth case loaded."

    # For now we download this from the web, but the YAML file might eventually be
    # added to the project file itself: https://github.com/linkml/linkml/issues/475
    jsonldContext = ContextGenerator(CRDCH_YAML_URI).serialize()
    jsonldContextAsDict = json.loads(jsonldContext)
    assert type(jsonldContextAsDict) is dict

    diagnoses = []
    for case in gdc_head_and_mouth:
        for diagnosis in case['diagnoses']:
            diagnosis_as_obj = transform_diagnosis(diagnosis, case)
            diagnoses.append(diagnosis_as_obj)
            as_json_str = json_dumper.dumps(diagnosis_as_obj, jsonldContextAsDict)
            assert type(as_json_str) is str
            as_json = json.loads(as_json_str)
            assert type(as_json) is dict

            # logging.warning(f'Diagnosis {diagnosis} from case {case} transformed into {diagnosis_as_obj}')

    as_json_str = json_dumper.dumps({
        '@graph': diagnoses,
        '@context': jsonldContextAsDict
    })
    assert type(as_json_str) is str
    as_json = json.loads(as_json_str)
    assert type(as_json) is dict

    with open('./head-and-mouth/diagnoses.jsonld', 'w') as f:
        f.write(as_json_str)

    # Convert JSON-LD into Turtle.
    g = rdflib.Graph()
    g.parse(data=as_json_str, format="json-ld")
    rdf_as_turtle = g.serialize(format="turtle").decode()
    with open('head-and-mouth/diagnoses.ttl', 'w') as file:
        file.write(rdf_as_turtle)
