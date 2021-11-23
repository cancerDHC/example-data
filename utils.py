# python package that contains CRDCH data model as Python dataclasses
import crdch_model

def codeable_concept(system, code, label=None, text=None, tags=[]):
    """Create a crdch_model.CodeableConcept for a given [single] system and code. """

    coding = crdch_model.Coding(system=system, code=code)

    if label is not None:
        coding.label = label

    if len(tags) > 0:
        coding.tag = tags

    cc = crdch_model.CodeableConcept(coding)

    if text is not None:
        cc.text = text

    return cc
