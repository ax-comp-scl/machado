# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Serializers."""
from rest_framework import serializers


class FileSerializer(serializers.Serializer):
    """File serializer."""

    file = serializers.FileField()

class LoadPublicationSerializer(serializers.Serializer):
    file = serializers.FileField()
    cpu = serializers.IntegerField(required=False, min_value=1, default=1, help_text="Number of threads")

class FastaSerializer(serializers.Serializer):
    file = serializers.FileField()
    organism = serializers.CharField(required=True, help_text="Species name (eg. Homo sapiens, Mus musculus)")
    soterm = serializers.CharField(required=True, help_text="SO Sequence Ontology Term (eg. chromosome, assembly)")
    description = serializers.CharField(required=False, help_text="Description")
    url = serializers.CharField(required=False, help_text="URL")
    doi = serializers.CharField(required=False, help_text="DOI of a reference stored using load_publication (eg. 10.1111/s12122-012-1313-4)")
    nosequence = serializers.CharField(required=False, help_text="Don't load the sequences")
    cpu = serializers.IntegerField(required=False, min_value=1, default=1, help_text="Number of threads")

class LoadFeatureAnnotationSerializer(serializers.Serializer):
    file = serializers.FileField()
    organism = serializers.CharField(required=True, help_text="Species name (eg. Homo sapiens, Mus musculus)")
    soterm = serializers.CharField(required=True, help_text="SO Sequence Ontology Term (eg. mRNA, polypeptide)")
    cvterm = serializers.CharField(required=True, help_text="cvterm.name from cv feature_property. (eg. display, note, product, alias, ontology_term, annotation)")
    doi = serializers.CharField(required=False, help_text="DOI of a reference stored using load_publication (eg. 10.1111/s12122-012-1313-4)")
    cpu = serializers.IntegerField(required=False, min_value=1, default=1, help_text="Number of threads")

class LoadFeatureSequenceSerializer(serializers.Serializer):
    file = serializers.FileField()
    organism = serializers.CharField(required=True, help_text="Species name (eg. Homo sapiens, Mus musculus)")
    soterm = serializers.CharField(required=True, help_text="SO Sequence Ontology Term (eg. mRNA, polypeptide)")
    cpu = serializers.IntegerField(required=False, min_value=1, default=1, help_text="Number of threads")

class LoadFeaturePublicationSerializer(serializers.Serializer):
    file = serializers.FileField()
    organism = serializers.CharField(required=False, help_text="Species name (eg. Homo sapiens, Mus musculus)")
    cpu = serializers.IntegerField(required=False, min_value=1, default=1, help_text="Number of threads")

class LoadFeatureDBxRefSerializer(serializers.Serializer):
    file = serializers.FileField()
    organism = serializers.CharField(required=True, help_text="Species name (eg. Homo sapiens, Mus musculus)")
    soterm = serializers.CharField(required=True, help_text="SO Sequence Ontology Term (eg. mRNA, polypeptide)")
    cpu = serializers.IntegerField(required=False, min_value=1, default=1, help_text="Number of threads")

class OrganismSerializer(serializers.Serializer):
    """Organism serializer."""

    genus = serializers.CharField(required=True, help_text="The genus of the organism.")
    species = serializers.CharField(
        required=True, help_text="The species of the organism."
    )
    abbreviation = serializers.CharField(
        required=False, help_text="Abbreviation of the organism name."
    )
    common_name = serializers.CharField(
        required=False, help_text="Common name of the organism."
    )
    infraspecific_name = serializers.CharField(
        required=False, help_text="Infraspecific name of the organism."
    )
    comment = serializers.CharField(
        required=False, help_text="Additional comments about the organism."
    )
