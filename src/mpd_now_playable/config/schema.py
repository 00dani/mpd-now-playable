from json import dump
from pathlib import Path
from pprint import pp
from typing import Any, Mapping

from apischema.json_schema import JsonSchemaVersion, deserialization_schema

from .model import Config


def generate() -> Mapping[str, Any]:
	return deserialization_schema(Config, version=JsonSchemaVersion.DRAFT_7)


def write() -> None:
	schema = dict(generate())
	schema["$id"] = Config.schema.human_repr()

	schema_file = Path(__file__).parent / Config.schema.name
	print(f"Writing this schema to {schema_file}")
	pp(schema)
	with open(schema_file, "w") as fp:
		dump(schema, fp, indent="\t", sort_keys=True)
		fp.write("\n")


if __name__ == "__main__":
	write()
