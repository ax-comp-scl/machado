# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load views."""
from django.conf import settings
from django.core.management import call_command

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from machado.api.serializers import load as loadSerializers

from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from threading import Thread

class OrganismViewSet(viewsets.GenericViewSet):
    """ViewSet for loading organism."""

    serializer_class = loadSerializers.OrganismSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load organism"
    operation_description = operation_summary + "<br /><br />"
    if hasattr(settings, "MACHADO_EXAMPLE_ORGANISM_COMMON_NAME"):
        operation_description += "<b>Example:</b><br />common_name={}".format(
            settings.MACHADO_EXAMPLE_ORGANISM_COMMON_NAME
        )

    request_body = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "genus": openapi.Schema(type=openapi.TYPE_STRING, description="Genus"),
            "species": openapi.Schema(type=openapi.TYPE_STRING, description="Species"),
            "infraspecific_name": openapi.Schema(
                type=openapi.TYPE_STRING, description="Infraspecific name"
            ),
            "abbreviation": openapi.Schema(
                type=openapi.TYPE_STRING, description="Abbreviation"
            ),
            "common_name": openapi.Schema(
                type=openapi.TYPE_STRING, description="Common name"
            ),
            "comment": openapi.Schema(type=openapi.TYPE_STRING, description="Comment"),
        },
    )

    @swagger_auto_schema(
        request_body=request_body,
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    def create(self, request):
        """Handle the POST request for loading organism."""
        genus = request.data.get("genus")
        species = request.data.get("species")
        abbreviation = request.data.get("abbreviation")
        common_name = request.data.get("common_name")
        infraspecific_name = request.data.get("infraspecific_name")
        comment = request.data.get("comment")

        if not genus or not species:
            return Response(
                {"error": "Genus and species are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        thread = Thread(
            target=call_command,
            args=("insert_organism",),
            kwargs=(
                {
                    "genus": genus,
                    "species": species,
                    "abbreviation": abbreviation,
                    "common_name": common_name,
                    "infraspecific_name": infraspecific_name,
                    "comment": comment,
                }
            ),
            daemon=True,
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "insert_organism",
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request):
        """Handle the DELETE request for loading organism."""
        organism = request.data.get("organism")

        if not organism:
            return Response(
                {"error": "Organism is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        thread = Thread(
            target=call_command,
            args=("remove_organism",),
            kwargs=(
                {
                    "organism": organism
                }
            ),
            daemon=True
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "remove_organism",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

class RelationsOntologyViewSet(viewsets.GenericViewSet):
    """ViewSet for loading relations ontology."""

    serializer_class = loadSerializers.FileSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load relations ontology"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.com/oborel/obo-relations</li>"
    operation_description += "<li>File: ro.obo</li>"

    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="ro.obo file",
        required=True,
        type=openapi.TYPE_FILE,
    )

    @swagger_auto_schema(
        manual_parameters=[
            file_param,
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    def create(self, request):
        """Handle the POST request for loading organism."""
        in_memory_file = request.FILES["file"]

        print(in_memory_file.name)

        destination = open(f"/tmp/{in_memory_file.name}", "wt")
        destination.write(in_memory_file.read().decode("ascii", "ignore"))
        destination.close()

        thread = Thread(
            target=call_command,
            args=("load_relations_ontology",),
            kwargs=(
                {
                    "file": f"/tmp/{in_memory_file.name}",
                    "verbosity": 0,
                }
            ),
            daemon=True,
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "load_relations_ontology",
                "file": f"/tmp/{in_memory_file.name}",
            },
            status=status.HTTP_200_OK,
        )
    def destroy(self, request):
        """Handle the DELETE request for loading ontology."""
        cvname = request.data.get("name")

        if not cvname:
            return Response(
                {"error": "Name is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        thread = Thread(
            target=call_command,
            args=("remove_ontology",),
            kwargs=(
                {
                    "name": cvname
                }
            ),
            daemon=True
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "remove_ontology",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

class PublicationViewSet(viewsets.GenericViewSet):
    """ViewSet for loading publications from .bib file."""

    serializer_class = loadSerializers.LoadPublicationSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load publications from BibTeX file"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>File: reference.bib</li>"

    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="BibTeX file",
        required=True,
        type=openapi.TYPE_FILE,
    )

    @swagger_auto_schema(
        manual_parameters=[file_param],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    def create(self, request):
        """Handle the POST request for loading publication."""
        uploaded_file = request.FILES.get("file")
        cpu = int(request.data.get("cpu", 1))

        if not uploaded_file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Salvar arquivo temporariamente
        file_path = f"/tmp/{uploaded_file.name}"
        with open(file_path, "wb") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        # Rodar comando em segundo plano
        thread = Thread(
            target=call_command,
            args=("load_publication",),
            kwargs={
                "file": file_path,
                "cpu": cpu,
                "verbosity": 0,
            },
            daemon=True,
        )
        thread.start()

        return Response(
            {
                "status": "Submitted successfully",
                "call_command": "load_publication",
                "file": file_path,
                "cpu": cpu,
            },
            status=status.HTTP_200_OK,
        )

class SequenceOntologyViewSet(viewsets.GenericViewSet):
    """ViewSet for loading sequence ontology."""

    serializer_class = loadSerializers.FileSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load sequence ontology"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.com/The-Sequence-Ontology/SO-Ontologies</li>"
    operation_description += "<li>File: so.obo</li>"

    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="so.obo file",
        required=True,
        type=openapi.TYPE_FILE,
    )

    @swagger_auto_schema(
        manual_parameters=[
            file_param,
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )

    def create(self, request):
        """Handle the POST request for loading sequence ontology."""
        in_memory_file = request.FILES["file"]

        print(in_memory_file.name)

        destination = open(f"/tmp/{in_memory_file.name}", "wt")
        destination.write(in_memory_file.read().decode("ascii", "ignore"))
        destination.close()

        thread = Thread(
            target=call_command,
            args=("load_sequence_ontology",),
            kwargs=(
                {
                    "file": f"/tmp/{in_memory_file.name}",
                    "verbosity": 0,
                }
            ),
            daemon=True,
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "load_sequence_ontology",
                "file": f"/tmp/{in_memory_file.name}",
            },
            status=status.HTTP_200_OK,
        )
    def destroy(self, request):
        """Handle the DELETE request for loading ontology."""
        cvname = request.data.get("name")

        if not cvname:
            return Response(
                {"error": "Name is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        thread = Thread(
            target=call_command,
            args=("remove_ontology",),
            kwargs=(
                {
                    "name": cvname
                }
            ),
            daemon=True
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "remove_ontology",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

class GeneOntologyViewSet(viewsets.GenericViewSet):
    """ViewSet for loading gene ontology."""

    serializer_class = loadSerializers.FileSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load gene ontology"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://current.geneontology.org/ontology/</li>" # o link está cagado
    operation_description += "<li>File: go.obo</li>"

    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="go.obo file",
        required=True,
        type=openapi.TYPE_FILE,
    )

    @swagger_auto_schema(
        manual_parameters=[
            file_param,
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    def create(self, request):
        """Handle the POST request for loading organism."""
        in_memory_file = request.FILES["file"]

        destination = open(f"/tmp/{in_memory_file.name}", "wt")
        destination.write(in_memory_file.read().decode("ascii", "ignore"))
        destination.close()

        thread = Thread(
            target=call_command,
            args=("load_gene_ontology",),
            kwargs=(
                {
                    "file": f"/tmp/{in_memory_file.name}",
                    "verbosity": 0,
                }
            ),
            daemon=True,
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "load_gene_ontology",
                "file": f"/tmp/{in_memory_file.name}",
            },
            status=status.HTTP_200_OK,
        )
    def destroy(self, request):
        """Handle the DELETE request for loading ontology."""
        cvname = request.data.get("name")

        if not cvname:
            return Response(
                {"error": "Name is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        thread = Thread(
            target=call_command,
            args=("remove_ontology",),
            kwargs=(
                {
                    "name": cvname
                }
            ),
            daemon=True
        )

        thread.start()

        return Response(
            {
                "status": "Submited successfully",
                "call_command": "remove_ontology",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

class FastaViewSet(viewsets.GenericViewSet):
    """ViewSet for loading fasta"""

    serializer_class = loadSerializers.FastaSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load fasta"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.comhttps//github.com/lmb-embrapa/machado/blob/master/extras/sample.tar.gz/lmb-embrapa/machado/blob/master/extras/sample.tar.gz</li>"
    operation_description += "<li>File: organism_chrs.fa/li>"

    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="FASTA File",
        required=True,
        type=openapi.TYPE_FILE,
    )

    organism_param = openapi.Parameter(
        "organism",
        openapi.IN_QUERY,
        description="Species name (eg. Homo sapiens, Mus musculus)",
        required=True,
        type=openapi.TYPE_STRING
    )

    soterm_param = openapi.Parameter(
        "soterm",
        openapi.IN_QUERY,
        description="SO Sequence Ontology Term (eg. chromosome, assembly) *",
        required=True,
        type=openapi.TYPE_STRING
    )

    description_param = openapi.Parameter(
        "description",
        openapi.IN_QUERY,
        description="DESCRIPTION",
        required=False,
        type=openapi.TYPE_STRING
    )

    url_param = openapi.Parameter(
        "url",
        openapi.IN_QUERY,
        description="URL",
        required=False,
        type=openapi.TYPE_STRING
    )

    doi_param = openapi.Parameter(
        "doi",
        openapi.IN_QUERY,
        description="DOI of a reference stored using load_publication (eg. 10.1111/s12122-012-1313-4)",
        required=False,
        type=openapi.TYPE_STRING
    )

    nosequence_param = openapi.Parameter(
        "nosequence",
        openapi.IN_QUERY,
        description="Don't load the sequences",
        required=False,
        type=openapi.TYPE_BOOLEAN
    )

    cpu_param = openapi.Parameter(
        "cpu",
        openapi.IN_QUERY,
        description="Number of threads",
        required=False,
        type=openapi.TYPE_INTEGER
    )
    
    @swagger_auto_schema(
        manual_parameters=[
            file_param,
            organism_param,
            soterm_param,
            description_param,
            url_param,
            doi_param,
            nosequence_param,
            cpu_param
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    def create(self, request):
        """Handle the POST request for loading fasta."""

        file = request.FILES.get("file")
        organism = request.data.get("organism", "")
        soterm = request.data.get("soterm", "")
        description = request.data.get("description", "")
        url = request.data.get("url", "")
        doi = request.data.get("doi", "")
        nosequence = request.data.get("nosequence", "")
        cpu = int(request.data.get("cpu", 1))

        if not file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(organism):
            return Response(
                {"error": "Organism is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not bool(soterm):
            return Response(
                {"error": "soterm  is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_path = f"/tmp/{file.name}"
        with open(file_path, "wb") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        thread = Thread(
            target=call_command,
            args=("load_fasta",),
            kwargs={
                "file": file_path,
                "organism": organism,
                "soterm": soterm,
                "description": description,
                "url": url,
                "doi": doi,
                "nosequence": nosequence,
                "cpu": cpu,
                "verbosity": 0,
            },
            daemon=True,
        )

        thread.start()

        return Response(
            {
                "status": "Submitted successfully",
                "call_command": "load_fasta",
                "file": file_path,
                "organism": organism,
                "soterm": soterm,
                "description": description,
                "url": url,
                "doi": doi,
                "nosequence": nosequence,
                "cpu": cpu,
            },
            status=status.HTTP_200_OK,
        )

class FeatureAnnotationViewSet(viewsets.GenericViewSet):
    """ViewSet for loading feature annotation"""
    serializer_class = loadSerializers.LoadFeatureAnnotationSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load feature annotation"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.comhttps//github.com/lmb-embrapa/machado/blob/master/extras/sample.tar.gz/lmb-embrapa/machado/blob/master/extras/sample.tar.gz</li>"
    operation_description += "<li>File: feature_annotation.tab/li>"
    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="Feature annotation File",
        required=True,
        type=openapi.TYPE_FILE,
    )
    organism_param = openapi.Parameter(
        "organism",
        openapi.IN_QUERY,
        description="Species name (eg. Homo sapiens, Mus musculus)",
        required=True,
        type=openapi.TYPE_STRING
    )

    soterm_param = openapi.Parameter(
        "soterm",
        openapi.IN_QUERY,
        description="SO Sequence Ontology Term (eg. chromosome, assembly) *",
        required=True,
        type=openapi.TYPE_STRING
    )

    cvterm_param = openapi.Parameter(
        "cvterm",
        openapi.IN_QUERY,
        description="cvterm.name from cv feature_property. (eg. display, note, product, alias, ontology_term, annotation)",
        required=True,
        type=openapi.TYPE_STRING
    )

    doi_param = openapi.Parameter(
        "doi",
        openapi.IN_QUERY,
        description="DOI of a reference stored using load_publication (eg. 10.1111/s12122-012-1313-4)",
        required=False,
        type=openapi.TYPE_STRING
    )

    cpu_param = openapi.Parameter(
        "cpu",
        openapi.IN_QUERY,
        description="Number of threads",
        required=False,
        type=openapi.TYPE_INTEGER
    )

    @swagger_auto_schema(
        manual_parameters=[
            file_param,
            organism_param,
            soterm_param,
            cvterm_param,
            doi_param,
            cpu_param
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )

    def create(self, request):
        """Handle the POST request for loading feature annotation."""
        file = request.FILES.get("file")
        organism = request.data.get("organism", "")
        soterm = request.data.get("soterm", "")
        cvterm = request.data.get("cvterm", "")
        doi = request.data.get("doi", "")
        cpu = int(request.data.get("cpu", 1))

        if not file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(organism):
            return Response(
                {"error": "Organism is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(soterm):
            return Response(
                {"error": "soterm is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if not bool(cvterm):
            return Response(
                {"error": "cvterm is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_path = f"/tmp/{file.name}"
        with open(file_path, "wb") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        thread = Thread(
            target=call_command,
            args=("load_feature_annotation",),
            kwargs={
                "file": file_path,
                "organism": organism,
                "soterm": soterm,
                "cvterm": cvterm,
                "doi": doi,
                "cpu": cpu,
                "verbosity": 0,
            },
            daemon=True,
        )
        thread.start()

        return Response(
            {
                "status": "Submitted successfully",
                "call_command": "load_feature_annotation",
                "file": file_path,
                "organism": organism,
                "soterm": soterm,
                "cvterm": cvterm,
                "doi": doi,
                "cpu": cpu,
            },
            status=status.HTTP_200_OK,)

class FeatureSequenceViewSet(viewsets.GenericViewSet):
    """ViewSet for loading feature sequence"""
    serializer_class = loadSerializers.LoadFeatureSequenceSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load feature sequence"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.comhttps//github.com/lmb-embrapa/machado/blob/master/extras/sample.tar.gz/lmb-embrapa/machado/blob/master/extras/sample.tar.gz</li>"
    operation_description += "<li>File: Athaliana_transcripts.fasta/li>"
    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="Feature sequence File",
        required=True,
        type=openapi.TYPE_FILE,
    )
    organism_param = openapi.Parameter(
        "organism",
        openapi.IN_QUERY,
        description="Species name (eg. Homo sapiens, Mus musculus)",
        required=True,
        type=openapi.TYPE_STRING
    )

    soterm_param = openapi.Parameter(
        "soterm",
        openapi.IN_QUERY,
        description="SO Sequence Ontology Term (eg. chromosome, assembly) *",
        required=True,
        type=openapi.TYPE_STRING
    )

    cpu_param = openapi.Parameter(
        "cpu",
        openapi.IN_QUERY,
        description="Number of threads",
        required=False,
        type=openapi.TYPE_INTEGER
    )

    @swagger_auto_schema(
        manual_parameters=[
            file_param,
            organism_param,
            soterm_param,
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )

    def create(self, request):
        """Handle the POST request for loading feature sequence."""
        file = request.FILES.get("file")
        organism = request.data.get("organism", "")
        soterm = request.data.get("soterm", "")
        cpu = int(request.data.get("cpu", 1))

        if not file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(organism):
            return Response(
                {"error": "Organism is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(soterm):
            return Response(
                {"error": "soterm is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_path = f"/tmp/{file.name}"
        with open(file_path, "wb") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        thread = Thread(
            target=call_command,
            args=("load_feature_sequence",),
            kwargs={
                "file": file_path,
                "organism": organism,
                "soterm": soterm,
                "verbosity": 0,
            },
            daemon=True,
        )
        thread.start()

        return Response(
            {
                "status": "Submitted successfully",
                "call_command": "load_feature_sequence",
                "file": file_path,
                "organism": organism,
                "soterm": soterm,
                "cpu": cpu,
            },
            status=status.HTTP_200_OK,)

class FeaturePublicationViewSet(viewsets.GenericViewSet):
    """ViewSet for loading feature publication"""
    serializer_class = loadSerializers.LoadFeaturePublicationSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load feature publication"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.comhttps//github.com/lmb-embrapa/machado/blob/master/extras/sample.tar.gz/lmb-embrapa/machado/blob/master/extras/sample.tar.gz</li>"
    operation_description += "<li>File: feature_publication.tab/li>"
    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="Feature publication File",
        required=True,
        type=openapi.TYPE_FILE,
    )
    organism_param = openapi.Parameter(
        "organism",
        openapi.IN_QUERY,
        description="Species name (eg. Homo sapiens, Mus musculus)",
        required=False,
        type=openapi.TYPE_STRING
    )

    cpu_param = openapi.Parameter(
        "cpu",
        openapi.IN_QUERY,
        description="Number of threads",
        required=False,
        type=openapi.TYPE_INTEGER
    )

    @swagger_auto_schema(
        manual_parameters=[
            file_param,
            organism_param,
            cpu_param
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )

    def create(self, request):
        """Handle the POST request for loading feature publication."""
        file = request.FILES.get("file")
        organism = request.data.get("organism", "")
        cpu = int(request.data.get("cpu", 1))

        if not file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_path = f"/tmp/{file.name}"
        with open(file_path, "wb") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        thread = Thread(
            target=call_command,
            args=("load_feature_publication",),
            kwargs={
                "file": file_path,
                "organism": organism,
                "cpu": cpu,
                "verbosity": 0,
            },
            daemon=True,
        )
        thread.start()

        return Response(
            {
                "status": "Submitted successfully",
                "call_command": "load_feature_publication",
                "file": file_path,
                "organism": organism,
                "cpu": cpu,
            },
            status=status.HTTP_200_OK,)

class FeatureDBxRefViewSet(viewsets.GenericViewSet):
    """ViewSet for loading feature dbxrefs"""
    serializer_class = loadSerializers.LoadFeatureDBxRefSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load feature dbxrefs"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.comhttps//github.com/lmb-embrapa/machado/blob/master/extras/sample.tar.gz/lmb-embrapa/machado/blob/master/extras/sample.tar.gz</li>"
    operation_description += "<li>File: feature_dbxrefs.tab/li>"
    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="Feature dbxrefs File",
        required=True,
        type=openapi.TYPE_FILE,
    )
    organism_param = openapi.Parameter(
        "organism",
        openapi.IN_QUERY,
        description="Species name (eg. Homo sapiens, Mus musculus)",
        required=True,
        type=openapi.TYPE_STRING
    )

    soterm_param = openapi.Parameter(
        "soterm",
        openapi.IN_QUERY,
        description="SO Sequence Ontology Term (eg. chromosome, assembly) *",
        required=True,
        type=openapi.TYPE_STRING
    )

    cpu_param = openapi.Parameter(
        "cpu",
        openapi.IN_QUERY,
        description="Number of threads",
        required=False,
        type=openapi.TYPE_INTEGER
    )

    @swagger_auto_schema(
        manual_parameters=[
            file_param,
            organism_param,
            soterm_param,
            cpu_param
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )

    def create(self, request):
        """Handle the POST request for loading feature dbxrefs."""
        file = request.FILES.get("file")
        organism = request.data.get("organism", "")
        soterm = request.data.get("soterm", "")
        cpu = int(request.data.get("cpu", 1))

        if not file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(organism):
            return Response(
                {"error": "Organism is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(soterm):
            return Response(
                {"error": "soterm is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_path = f"/tmp/{file.name}"
        with open(file_path, "wb") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        thread = Thread(
            target=call_command,
            args=("load_feature_dbxrefs",),
            kwargs={
                "file": file_path,
                "organism": organism,
                "soterm": soterm,
                "verbosity": 0,
            },
            daemon=True,
        )
        thread.start()

        return Response(
            {
                "status": "Submitted successfully",
                "call_command": "load_feature_dbxrefs",
                "file": file_path,
                "organism": organism,
                "soterm": soterm,
                "cpu": cpu,
            },
            status=status.HTTP_200_OK,)
    
class GFFViewSet(viewsets.GenericViewSet):
    """ViewSet for loading GFF"""
    serializer_class = loadSerializers.GFFSerializer
    permission_classes = [IsAuthenticated]
    operation_summary = "Load GFF"
    operation_description = operation_summary + "<br /><br />"
    operation_description += "<li>URL: https://github.comhttps//github.com/lmb-embrapa/machado/blob/master/extras/sample.tar.gz/lmb-embrapa/machado/blob/master/extras/sample.tar.gz</li>"
    operation_description += "<li>File: organism_genes_sorted.gff3.gz</li>"

    file_param = openapi.Parameter(
        "file",
        openapi.IN_QUERY,
        description="GFF3 genome file indexed with tabix",
        required=True,
        type=openapi.TYPE_FILE,
    )

    organism_param = openapi.Parameter(
        "organism",
        openapi.IN_QUERY,
        description="Species name (eg. Homo sapiens, Mus musculus)",
        required=True,
        type=openapi.TYPE_STRING
    )

    ignore_param = openapi.Parameter(
        "ignore",
        openapi.IN_QUERY,
        description="List of feature types to ignore (eg. chromosome scaffold)",
        required=False,
        type=openapi.TYPE_STRING
    )

    doi_param = openapi.Parameter(
        "doi",
        openapi.IN_QUERY,
        description="DOI of a reference stored using load_publication (eg. 10.1111/s12122-012-1313-4)",
        required=False,
        type=openapi.TYPE_STRING
    )

    qtl_param = openapi.Parameter(
        "qtl",
        openapi.IN_QUERY,
        description="Set this flag to handle GFF files from QTLDB",
        required=False,
        type=openapi.TYPE_BOOLEAN
    )

    cpu_param = openapi.Parameter(
        "cpu",
        openapi.IN_QUERY,
        description="Number of threads",
        required=False,
        default=1,
        type=openapi.TYPE_INTEGER
    )
    
    @swagger_auto_schema(
        manual_parameters=[
            file_param,
            organism_param,
            ignore_param,
            doi_param,
            qtl_param,
            cpu_param
        ],
        operation_summary=operation_summary,
        operation_description=operation_description,
    )
    def create(self, request):
        """Handle the POST request for loading GFF."""

        file = request.FILES.get("file")
        organism = request.data.get("organism", "")
        ignore = request.data.get("ignore", "")
        doi = request.data.get("doi", "")
        qtl = request.data.get("qtl", "")
        cpu = int(request.data.get("cpu", 1))

        if not file:
            return Response(
                {"error": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(organism):
            return Response(
                {"error": "Organism is a required field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_path = f"/tmp/{file.name}"
        with open(file_path, "wb") as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        thread = Thread(
            target=call_command,
            args=("load_gff",),
            kwargs={
                "file": file_path,
                "organism": organism,
                "ignore": ignore,
                "doi": doi,
                "qtl": qtl,
                "cpu": cpu,
                "verbosity": 0,
            },
            daemon=True,
        )

        thread.start()

        return Response(
            {
                "status": "Submitted successfully",
                "call_command": "load_gff",
                "file": file_path,
                "organism": organism,
                "ignore": ignore,
                "doi": doi,
                "qtl": qtl,
                "cpu": cpu,
            },
            status=status.HTTP_200_OK,
        )