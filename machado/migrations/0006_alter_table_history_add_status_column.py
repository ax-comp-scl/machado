# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Create database from chado default_schema.sql."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("machado", "0001_initial"),
        ("machado", "0002_add_index"),
        ("machado", "0003_add_multispecies"),
        ("machado", "0004_create_history"),
        ("machado", "0005_add_db_url"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE history ADD status CHAR(1)"
        ),
    ]