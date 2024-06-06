# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
from owlready2 import get_ontology
ontology = get_ontology('/Users/marekstrba/Documents/skola/bakalarka/malont/MALOnt.owl').load()


def extract_classes(ontology):
    return {cls.name.lower() for cls in ontology.classes()}


def extract_properties(ontology):
    properties = set()
    for prop in ontology.object_properties():
        properties.add(prop.name.lower())
    for prop in ontology.data_properties():
        properties.add(prop.name.lower())
    return properties


def extract_individuals(ontology):
    individuals = set()
    for individual in ontology.individuals():
        individuals.add(individual.name.lower())
    return individuals


def extract_ontology_terms(ontology):
    terms = set()
    terms.update(extract_classes(ontology))
    terms.update(extract_properties(ontology))
    terms.update(extract_individuals(ontology))
    return terms


ontology_terms = extract_ontology_terms(ontology)