"""Utility script for investigating Dynamics API. Requires environment variables to be set properly."""

import json

from django.core.management.base import BaseCommand, CommandParser

from ... import DynamicsClient


class Command(BaseCommand):
    help = (
        "Small utility script to help with investigating the Dynamics API. "
        "Include quotes if you wish to add more than one query option with '&'."
    )

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
            "-q",
            help="Dynamics API query.",
            default="",
        )
        parser.add_argument(
            "--to-file",
            action="store_true",
            help="Save data to file instad of printing it.",
        )
        parser.add_argument(
            "--fetch-schema",
            action="store_true",
            help="Save Dynamics schema to file instead of fetching anything.",
        )

    def handle(self, *args, **options):

        api = DynamicsClient.from_environment()

        if options["fetch_schema"]:
            schema = api.fetch_schema()
            with open(f"dynamics_schema.xml", "w+") as f:
                f.write(schema)
            return

        query = options.get("q")
        api.show_annotations = True
        api.table = query
        result = api.GET()

        if options["to_file"]:
            with open(f"dynamic_data_query__{query}.json", "w+") as f:
                json.dump(result, f, indent=2, sort_keys=True)
        else:
            print(json.dumps(result, sort_keys=True, indent=2))
