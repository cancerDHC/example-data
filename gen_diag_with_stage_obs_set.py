import crdch_model as cm
from linkml_runtime.dumpers import yaml_dumper

ncit_sys_url = "http://ncithesaurus.nci.nih.gov/"
harmonized_tag = "harmonized"
diagnosis_fn = "gen_diag_with_stage_obs_set.yaml"

stage_obs_set = cm.CancerStageObservationSet()

obs_type_coding = cm.Coding(code="C25605", system=ncit_sys_url, label="Overall")
obs_type_coding.tag.append(harmonized_tag)
obs_type_cc = cm.CodeableConcept(coding=obs_type_coding)

stage_value_coding = cm.Coding(code="C96258", system=ncit_sys_url, label="FIGO Stage IIIC")
stage_value_coding.tag.append(harmonized_tag)
stage_value_cc = cm.CodeableConcept(coding=stage_value_coding)

stage_obs = cm.CancerStageObservation(observation_type=obs_type_cc, value_codeable_concept=stage_value_cc)

stage_obs_set.observations.append(stage_obs)

meth_type_coding = cm.Coding(code="C125738", system=ncit_sys_url, label="FIGO Stage")
meth_type_coding.tag.append(harmonized_tag)
meth_type_cc = cm.CodeableConcept(coding=meth_type_coding)

stage_obs_set.method_type.append(meth_type_cc)

diag = cm.Diagnosis()
diag.stage.append(stage_obs_set)

yaml_dumper.dump(diag, to_file=diagnosis_fn)
