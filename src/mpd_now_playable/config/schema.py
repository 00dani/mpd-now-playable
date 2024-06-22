from json import dump
from pathlib import Path
from pprint import pp
from shutil import get_terminal_size
from typing import Any, Mapping

from apischema import schema, settings
from apischema.json_schema import JsonSchemaVersion, deserialization_schema
from apischema.schemas import Schema
from class_doc import extract_docs_from_cls_obj

from .model import Config


def field_base_schema(tp: type, name: str, alias: str) -> Schema | None:
	desc_lines = extract_docs_from_cls_obj(tp).get(name, [])
	if desc_lines:
		print((tp, name, alias))
		return schema(description=" ".join(desc_lines))
	return None


settings.base_schema.field = field_base_schema


def generate() -> Mapping[str, Any]:
	return deserialization_schema(
		Config,
		version=JsonSchemaVersion.DRAFT_7,
	)


def write() -> None:
	schema = dict(generate())
	schema["$id"] = Config.schema.human_repr()

	schema_file = Path(__file__).parent / Config.schema.name
	print(f"Writing this schema to {schema_file}")
	pp(schema, sort_dicts=True, width=get_terminal_size().columns)
	with open(schema_file, "w") as fp:
		dump(schema, fp, indent="\t", sort_keys=True)
		fp.write("\n")


if __name__ == "__main__":
	write()
