from typing import Callable

from mypy.plugin import ClassDefContext, Plugin
from mypy.plugins.common import add_attribute_to_class


def add_schema_classvars(ctx: ClassDefContext) -> None:
	api = ctx.api
	cls = ctx.cls
	URL = api.named_type("yarl.URL")
	Adapter = api.named_type(
		"pydantic.type_adapter.TypeAdapter", [api.named_type(cls.fullname)]
	)

	add_attribute_to_class(
		api,
		cls,
		"id",
		URL,
		final=True,
		is_classvar=True,
	)
	add_attribute_to_class(
		api,
		cls,
		"schema",
		Adapter,
		final=True,
		is_classvar=True,
	)


class SchemaDecoratorPlugin(Plugin):
	def get_class_decorator_hook(
		self, fullname: str
	) -> Callable[[ClassDefContext], None] | None:
		if fullname != "mpd_now_playable.tools.schema.define.schema":
			return None
		return add_schema_classvars


def plugin(version: str) -> type[SchemaDecoratorPlugin]:
	return SchemaDecoratorPlugin
