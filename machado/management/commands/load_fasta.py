# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Load FASTA file."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from Bio import SeqIO
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from machado.models import History
from machado.loaders.common import FileValidator, retrieve_organism
from machado.loaders.exceptions import ImportingError
from machado.loaders.sequence import SequenceLoader


class Command(BaseCommand):
    """Load FASTA file."""

    help = "Load FASTA file"

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--file", help="FASTA File", required=True, type=str)
        parser.add_argument(
            "--organism",
            help="Species name (eg. Homo sapiens, Mus musculus)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--soterm",
            help="SO Sequence Ontology Term (eg. chromosome, assembly)",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--nosequence",
            help="Don't load the sequence",
            required=False,
            action="store_true",
        )
        parser.add_argument("--cpu", help="Number of threads", default=1, type=int)
        parser.add_argument(
            "--description", help="Description", required=False, type=str
        )
        parser.add_argument("--url", help="URL", required=False, type=str)
        parser.add_argument(
            "--doi",
            help="DOI of the article reference to "
            "this sequence. E.g.: 10.1111/s12122-012-1313-4",
            required=False,
            type=str,
        )

    def handle(
        self,
        file: str,
        organism: str,
        soterm: str,
        nosequence: bool = False,
        cpu: int = 1,
        description: str = None,
        url: str = None,
        doi: str = None,
        verbosity: int = 1,
        **options
    ) -> None:
        """Execute the main function."""
        history_obj = History()
        history_obj.start(command="load_fasta", params=locals())

        if verbosity > 0:
            self.stdout.write("Preprocessing")

        try:
            FileValidator().validate(file)
            organism = retrieve_organism(organism)
        except ImportingError as e:
            history_obj.failure(description=str(e))
            raise CommandError(e)

        # retrieve only the file name
        filename = os.path.basename(file)
        try:
            sequence_file = SequenceLoader(
                filename=filename,
                organism=organism,
                description=description,
                url=url,
                doi=doi,
            )
        except ImportingError as e:
            raise CommandError(e)

        fasta_sequences = SeqIO.parse(open(file), "fasta")

        pool = ThreadPoolExecutor(max_workers=cpu)
        tasks = list()
        for fasta in fasta_sequences:
            tasks.append(
                pool.submit(
                    sequence_file.store_biopython_seq_record,
                    fasta,
                    soterm,
                    nosequence,
                )
            )
        if verbosity > 0:
            self.stdout.write("Loading")
        for task in tqdm(as_completed(tasks), total=len(tasks)):
            if task.result():
                raise (task.result())
        pool.shutdown()

        history_obj.success(description="Done")
        if verbosity > 0:
            self.stdout.write(self.style.SUCCESS("Done"))
