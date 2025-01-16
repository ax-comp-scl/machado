# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load relations ontology."""

import obonet
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.loaders.common import FileValidator
from machado.loaders.exceptions import ImportingError
from machado.loaders.ontology import OntologyLoader

from machado.models import History


class Command(BaseCommand):
    """Load relations ontology."""

    help = "Load Relations Ontology"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument(
            "--file",
            help="Relations Ontology file obo. "
            "Available at https://github.com/oborel/"
            "obo-relations",
            required=True,
            type=str,
        )

    def handle(self, file: str, verbosity: int = 1, **options):
        """Execute the main function."""
        history_obj = History()
        history_obj.start(command="load_relations_ontology", params=locals())
        try:
            FileValidator().validate(file)
        except ImportingError as e:
            history_obj.failure(description=str(e))
            raise CommandError(e)

        # Load the ontology file
        with open(file) as obo_file:
            G = obonet.read_obo(obo_file)

        if verbosity > 0:
            self.stdout.write("Preprocessing")

        cv_name = "relationship"

        # Initializing ontology
        ontology = OntologyLoader(cv_name)

        # Load typedefs as Dbxrefs and Cvterm
        if verbosity > 0:
            self.stdout.write("Loading typedefs")

        for data in tqdm(G.graph["typedefs"], disable=False if verbosity > 0 else True):
            ontology.store_type_def(data)

        history_obj.success(description="Done")
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
