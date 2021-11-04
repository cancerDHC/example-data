import crdch_model as cm
from linkml_runtime.dumpers import yaml_dumper

csos = cm.CancerStageObservationSet()

ncit_sys_url = "http://ncithesaurus.nci.nih.gov/"

ot = cm.Coding(code="C25605", system=ncit_sys_url, label="Overall")

ot.tag.append("harmonized")

otc = cm.CodeableConcept(coding=ot)

vc = cm.Coding(code="C96258", system=ncit_sys_url, label="FIGO Stage IIIC")

vc.tag.append("harmonized")

vcc = cm.CodeableConcept(coding=vc)

cso = cm.CancerStageObservation(observation_type=otc, value_codeable_concept=vcc)

csos.observations.append(cso)

mt = cm.Coding(code="C125738", system=ncit_sys_url, label="FIGO Stage")
mt.tag.append("harmonized")
mtc = cm.CodeableConcept(coding=mt)

csos.method_type.append(mtc)

d = cm.Diagnosis()

d.stage.append(csos)

yaml_dumper.dump(d, to_file="Diagnosis.yaml")
