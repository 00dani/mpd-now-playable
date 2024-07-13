from json import dump
from pathlib import Path

from class_doc import extract_docs_from_cls_obj
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode, JsonSchemaValue
from pydantic_core import core_schema as s
from rich.pretty import pprint

from .define import ModelWithSchema

__all__ = ("write",)


def write(model: ModelWithSchema) -> None:
	schema = model.schema.json_schema(schema_generator=MyGenerateJsonSchema)
	schema["$id"] = model.id.human_repr()
	schema_file = Path(__file__).parents[4] / "schemata" / model.id.name
	print(f"Writing this schema to {schema_file}")
	pprint(schema)
	with open(schema_file, "w") as fp:
		dump(schema, fp, indent="\t", sort_keys=True)
		fp.write("\n")


class MyGenerateJsonSchema(GenerateJsonSchema):
	def generate(
		self, schema: s.CoreSchema, mode: JsonSchemaMode = "validation"
	) -> dict[str, object]:
		json_schema = super().generate(schema, mode=mode)
		json_schema["$schema"] = self.schema_dialect
		return json_schema

	def default_schema(self, schema: s.WithDefaultSchema) -> JsonSchemaValue:
		result = super().default_schema(schema)
		if "default" in result and result["default"] is None:
			del result["default"]
		return result

	def dataclass_schema(self, schema: s.DataclassSchema) -> JsonSchemaValue:
		result = super().dataclass_schema(schema)
		docs = extract_docs_from_cls_obj(schema["cls"])
		for field, lines in docs.items():
			result["properties"][field]["description"] = " ".join(lines)
		return result

	def nullable_schema(self, schema: s.NullableSchema) -> JsonSchemaValue:
		return self.generate_inner(schema["schema"])

if __name__ == '__main__':
	from ...config.model import Config
	from ...song import Song
	write(Config)
	write(Song)
