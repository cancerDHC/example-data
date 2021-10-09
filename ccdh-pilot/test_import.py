#!/usr/bin/env python

#
# test_import.py - Import GDC and PDC data via public APIs and transform them into CRDC-H Instance data.
#

import json
import yaml

import linkml_runtime
from linkml_runtime.loaders.yaml_loader import YAMLLoader
from linkml_runtime.dumpers.yaml_dumper import YAMLDumper

import crdch_model

# Some general constants
EXAMPLE_PREFIX = 'gdc_head_and_mouth_example:'
GDC_URL = 'http://crdc.nci.nih.gov/gdc'
ICD10_URL = 'http://hl7.org/fhir/ValueSet/icd-10'


# Helper method to create a codeable concept.
def codeable_concept(system, code, label=None, text=None, tags=[]):
    coding = crdch_model.Coding(system=system, code=code)
    if label is not None:
        coding.label = label
    if len(tags) > 0:
        coding.tag = tags
    cc = crdch_model.CodeableConcept(coding)
    if text is not None:
        cc.text = text
    return cc


# Some codeable concepts we use repeatedly.
DAY = codeable_concept('http://ncithesaurus.nci.nih.gov', 'C25301', 'Day')


# Convert a single GDC sample into a CRDC-H specimen.
def create_specimen(gdc_sample, sample_index, gdc_diagnosis, diagnosis_index, gdc_case, case_index):
    specimen = crdch_model.Specimen(
        id=f'{EXAMPLE_PREFIX}case_{case_index}_sample_{sample_index}',
    )

    if gdc_sample.get('sample_id'):
        specimen.identifier = [crdch_model.Identifier(
            value=gdc_sample.get('sample_id'),
            system=GDC_URL
        )]

    # TODO: figure out what to do about associated_project.

    # Make sure this is right.
    if gdc_sample.get('submitter_id'):
        specimen.source_subject = crdch_model.Subject(
            id=f'{EXAMPLE_PREFIX}case_{case_index}_sample_{sample_index}_subject'
        )
        specimen.source_subject.identifier = [crdch_model.Identifier(
            value=gdc_sample.get('submitter_id'),
            system=GDC_URL
        )]

    if gdc_sample.get('sample_type'):
        specimen.source_material_type = codeable_concept(GDC_URL, gdc_sample.get('sample_type'))

    if gdc_sample.get('tissue_type'):
        specimen.general_tissue_pathology = codeable_concept(GDC_URL, gdc_sample.get('tissue_type'))

    if gdc_sample.get('tumor_code'):
        specimen.specific_tissue_pathology = codeable_concept(GDC_URL, gdc_sample.get('tumor_code'))

    if gdc_sample.get('tumor_descriptor'):
        specimen.tumor_status_at_collection = codeable_concept(GDC_URL, gdc_sample.get('tumor_descriptor'))

    return specimen


# Demonstrators
def test_import_gdc_head_and_mouth():
    with open('head-and-mouth/gdc-head-and-mouth.json') as file:
        gdc_head_and_mouth = json.load(file)

    # Each entry is a GDC case. To transform this into CRDC-H instance data, we need to
    # transform it as a series of diagnoses.
    diagnoses = []
    for (case_index, gdc_case) in enumerate(gdc_head_and_mouth):
        for (diag_index, gdc_diagnosis) in enumerate(gdc_case['diagnoses']):
            diagnosis = crdch_model.Diagnosis(
                id=f'{EXAMPLE_PREFIX}case_{case_index}_diagnosis_{diag_index}',
            )

            if gdc_case.get('submitter_id'):
                diagnosis.subject = crdch_model.Subject(
                    id=f'{EXAMPLE_PREFIX}case_{case_index}_diagnosis_{diag_index}_subject'
                )
                diagnosis.subject.identifier = [crdch_model.Identifier(
                    value=gdc_case.get('submitter_id'),
                    system=GDC_URL
                )]

            if gdc_diagnosis.get('diagnosis_id'):
                diagnosis.identifier = [crdch_model.Identifier(
                    value=gdc_diagnosis['diagnosis_id'],
                    system=GDC_URL
                )]

            if gdc_diagnosis.get('age_at_diagnosis'):
                # TODO: this is caused by a weird LinkML bug that means that setting properties directly does NOT
                # convert it into the correct base type. We should, uh, iron these out at some point.
                diagnosis.age_at_diagnosis = crdch_model.Quantity(unit=DAY)
                diagnosis.age_at_diagnosis.value_decimal = gdc_diagnosis['age_at_diagnosis']

            condition_codings = []
            if gdc_diagnosis.get('primary_diagnosis'):
                condition_codings.append(crdch_model.Coding(
                    system=GDC_URL,
                    code=gdc_diagnosis.get('primary_diagnosis'),
                    tag=['original']
                ))

            # TODO: double-check with DMH if this makes sense
            if gdc_diagnosis.get('icd_10_code'):
                condition_codings.append(crdch_model.Coding(
                    system=ICD10_URL,
                    code=gdc_diagnosis.get('icd_10_code'),
                    tag=['original']
                ))

            diagnosis.condition = crdch_model.CodeableConcept(coding=condition_codings)

            # if gdc_diagnosis.get('tissue_or_organ_of_origin'):
            #    diagnosis.primary_site = crdch_model.BodySite(
            #        site=codeable_concept(GDC_URL, gdc_diagnosis.get('tissue_or_organ_of_origin'), tags=['original'])
            #    )

            if gdc_diagnosis.get('ajcc_staging_system_edition'):
                observations = []

                def add_observation(type_code, type_label, stage_code):
                    if stage_code:
                        observations.append(crdch_model.CancerStageObservation(
                            observation_type=codeable_concept(GDC_URL, type_code, type_label, tags=['harmonized']),
                            value_codeable_concept=codeable_concept(GDC_URL, stage_code, stage_code, tags=['original'])
                        ))

                # TODO: I couldn't find AJCC v7 in NCIt, so these codes reference the 8th edition. Need to be fixed.
                # TODO: This is the first piece we should uncomment, because it triggers exactly the same error as when
                # we try loading these observations from YAML.
                # add_observation('C177555', 'AJCC v8 Clinical Stage', gdc_diagnosis.get('ajcc_clinical_stage'))
                # add_observation('C177606', 'AJCC v8 Clinical M Category', gdc_diagnosis.get('ajcc_clinical_m'))
                # add_observation('C177611', 'AJCC v8 Clinical N Category', gdc_diagnosis.get('ajcc_clinical_n'))
                # add_observation('C177635', 'AJCC v8 Clinical T Category', gdc_diagnosis.get('ajcc_clinical_t'))
                # add_observation('C177556', 'AJCC v8 Pathologic Stage', gdc_diagnosis.get('ajcc_pathologic_stage'))
                # add_observation('C177607', 'AJCC v8 Pathologic M Category', gdc_diagnosis.get('ajcc_pathologic_m'))
                # add_observation('C177612', 'AJCC v8 Pathologic N Category', gdc_diagnosis.get('ajcc_pathologic_n'))
                # add_observation('C177636', 'AJCC v8 Pathologic T Category', gdc_diagnosis.get('ajcc_pathologic_t'))

                diagnosis.stage = [crdch_model.CancerStageObservationSet(
                    method_type=codeable_concept(GDC_URL, gdc_diagnosis.get('ajcc_staging_system_edition'),
                                                 tags=['original']),
                    observations=observations
                )]

            # elif gdc_diagnosis.get('figo_stage'):

            # We assume that the diagnosis was created as its created_datetime.
            if gdc_diagnosis.get('created_datetime'):
                diagnosis.diagnosis_date = crdch_model.TimePoint(
                    date_time=gdc_diagnosis.get('created_datetime')
                )

            # Convert the specimen.
            specimens = [
                create_specimen(sample, sample_index, diagnosis, diag_index, gdc_case, case_index)
                for (sample_index, sample) in enumerate(gdc_case.get('samples') or [])
            ]
            if len(specimens) > 0:
                diagnosis.related_specimen = specimens

            # Write out the diagnosis.
            diagnoses.append({
                f'gdc_head_and_mouth_example_{case_index}_diagnosis_{diag_index}_diagnosis': {
                    'Provenance':
                        'Downloaded from the GDC Public API (see ' +
                        'https://github.com/cancerDHC/example-data/blob/main/head-and-mouth/Head%20and%20Mouth%20Cancer%20Datasets.ipynb ' +
                        'for instructions)."',
                    'Type': 'Diagnosis',
                    'Documentation': 'https://cancerdhc.github.io/ccdhmodel/v1.1/Diagnosis/',
                    'Example': diagnosis
                }
            })

    # Write out all diagnoses into a single YAML file in the imported-node-data directory.
    with open('ccdh-pilot/imported-node-data/gdc-head-and-mouth.yaml', 'w') as f:
        yaml.dump_all(diagnoses,
                      f, Dumper=yaml.SafeDumper,
                      sort_keys=False)
        linkml_runtime.utils.formatutils.remove_empty_items

    # yaml.dump(linkml_runtime.utils.formatutils.remove_empty_items(element, hide_protected_keys=True),
    #          Dumper=yaml.SafeDumper, sort_keys=False,
