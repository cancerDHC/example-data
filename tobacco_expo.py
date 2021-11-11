import crdch_model as cm
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.loaders import yaml_loader

obs_type_coding = cm.Coding(code="123", system="http://example.com/system")
obs_type_cc = cm.CodeableConcept(coding=obs_type_coding)
tobacco_expo = cm.TobaccoExposureObservation(observation_type=obs_type_cc)

print(tobacco_expo)

tobacco_expo_file = "tobacco_expo.yaml"

yaml_dumper.dump(tobacco_expo, to_file=tobacco_expo_file)

instantiated = yaml_loader.load(tobacco_expo_file, cm.TobaccoExposureObservation)

print(instantiated)
