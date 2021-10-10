#!/usr/bin/env python

#
# test_import.py - Import GDC and PDC data via public APIs and transform them into CRDC-H Instance data.
#

import json

import crdch_model
import yaml

# Some general constants
EXAMPLE_PREFIX = 'gdc_head_and_mouth_example:'
NCIT_URL = 'http://ncithesaurus.nci.nih.gov'
CCDH_URL = 'http://crdc.nci.nih.gov/ccdh'
GDC_URL = 'http://crdc.nci.nih.gov/gdc'
ICD10_URL = 'http://hl7.org/fhir/ValueSet/icd-10'


# Helper method to
def quantity(value_decimal, unit):
    q = crdch_model.Quantity(unit=unit)
    q.value_decimal = value_decimal
    return q


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
DAY = codeable_concept(NCIT_URL, 'C25301', 'Day', tags=['harmonized'])
MILLIGRAM = codeable_concept(NCIT_URL, 'C28253', 'Milligram', tags=['harmonized'])


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

    if gdc_sample.get('submitter_id'):
        submitter_identifier = crdch_model.Identifier(
            value=gdc_sample.get('submitter_id'),
            system=GDC_URL
        )
        if specimen.identifier:
            specimen.identifier.append(submitter_identifier)
        else:
            specimen.identifier = [submitter_identifier]

    # TODO: figure out what to do about associated_project.

    # Make sure this is right.
    if gdc_sample.get('submitter_id'):
        specimen.source_subject = crdch_model.Subject(
            id=f'{EXAMPLE_PREFIX}case_{case_index}_sample_{sample_index}_subject'
        )
        specimen.source_subject.identifier = [crdch_model.Identifier(
            value=gdc_sample.get('submitter_id'),
            system=f"{GDC_URL}#submitter_id"
        )]

    if gdc_case.get('case_id'):
        case_id = crdch_model.Identifier(
            value=gdc_case.get('case_id'),
            system=f"{GDC_URL}#case_id"
        )
        if specimen.source_subject:
            specimen.source_subject.identifier.append(case_id)
        else:
            specimen.source_subject = [case_id]

    # TODO: How do we calculate the Sample.type?

    if gdc_sample.get('sample_type'):
        specimen.source_material_type = codeable_concept(GDC_URL, gdc_sample.get('sample_type'))

    # TODO: get the project_id somehow.

    if gdc_sample.get('tissue_type'):
        specimen.general_tissue_pathology = codeable_concept(GDC_URL, gdc_sample.get('tissue_type'))

    if gdc_sample.get('tumor_code'):
        specimen.specific_tissue_pathology = codeable_concept(GDC_URL, gdc_sample.get('tumor_code'))

    if gdc_sample.get('tumor_descriptor'):
        specimen.tumor_status_at_collection = codeable_concept(GDC_URL, gdc_sample.get('tumor_descriptor'))

    if gdc_sample.get('current_weight'):
        specimen.quantity_measure = crdch_model.SpecimenQuantityObservation(
            observation_type=codeable_concept(NCIT_URL, 'C25208', 'Weight', tags=['harmonized']),
            value_quantity=quantity(gdc_sample.get('current_weight'), unit=MILLIGRAM)
        )

    # The following fields relate to the Specimen.creation_activity.

    if gdc_sample.get('days_to_collection'):
        date_ended = crdch_model.TimePoint(
            offset_from_index=quantity(gdc_sample.get('days_to_collection'), DAY),
            index_time_point=crdch_model.TimePoint(event_type=codeable_concept(NCIT_URL, 'C142714', 'Study Start', tags=['harmonized']))
        )
        specimen.creation_activity = crdch_model.SpecimenCreationActivity(date_ended=date_ended)

    if gdc_sample.get('initial_weight'):
        initial_weight = quantity(gdc_sample.get('initial_weight'), MILLIGRAM)
        if specimen.creation_activity:
            specimen.creation_activity.quantity_collected = initial_weight
        else:
            specimen.creation_activity = crdch_model.SpecimenCreationActivity(quantity_collected=initial_weight)

    if gdc_sample.get('biospecimen_anatomic_site'):
        biospecimen_anatomic_site = codeable_concept(GDC_URL, gdc_sample.get('biospecimen_anatomic_site'), label=gdc_sample.get('biospecimen_anatomic_site'))
        if specimen.creation_activity:
            specimen.creation_activity.collection_site = crdch_model.BodySite(site=biospecimen_anatomic_site)
        else:
            specimen.creation_activity = crdch_model.SpecimenCreationActivity(collection_site=crdch_model.BodySite(site=biospecimen_anatomic_site))

    if gdc_sample.get('time_between_excision_and_freezing'):
        time_obs = crdch_model.ExecutionTimeObservation(
            observation_type=codeable_concept(CCDH_URL, 'time_between_excision_and_freezing', label='time_between_excision_and_freezing')
        )
        if specimen.creation_activity:
            specimen.creation_activity.execution_time_observation = time_obs
        else:
            specimen.creation_activity = crdch_model.SpecimenCreationActivity(execution_time_observation=time_obs)

    # The following fields relate to the Specimen.processing_activity.
    if gdc_sample.get('preservation_method'):
        specimen.processing_activity = [
            crdch_model.SpecimenProcessingActivity(activity_type=codeable_concept(GDC_URL, gdc_sample.get('preservation_method')))
        ]

    if gdc_sample.get('freezing_method'):
        method_type = codeable_concept(GDC_URL, gdc_sample.get('freezing_method'))
        if len(specimen.processing_activity) > 0:
            specimen.processing_activity[0].method_type = method_type
        else:
            specimen.processing_activity = [crdch_model.SpecimenProcessingActivity(method_type=method_type)]

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

            if gdc_diagnosis.get('diagnosis_id'):
                diagnosis.identifier = [crdch_model.Identifier(
                    value=gdc_diagnosis['diagnosis_id'],
                    system=f"{GDC_URL}#diagnosis_id"
                )]

            diagnosis.subject = crdch_model.Subject(
                id=f'{EXAMPLE_PREFIX}case_{case_index}'
            )

            if gdc_case.get('case_id'):
                diagnosis.subject.identifier = [crdch_model.Identifier(
                    value=gdc_case.get('case_id'),
                    system=f"{GDC_URL}#case_id"
                )]

                if gdc_case.get('submitter_id'):
                    diagnosis.subject.identifier.append(crdch_model.Identifier(
                        value=gdc_case.get('submitter_id'),
                        system=f"{GDC_URL}#submitter_id"
                    ))

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

    # yaml.dump(linkml_runtime.utils.formatutils.remove_empty_items(element, hide_protected_keys=True),
    #          Dumper=yaml.SafeDumper, sort_keys=False,
