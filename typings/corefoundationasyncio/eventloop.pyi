import asyncio

class CoreFoundationEventLoop(asyncio.SelectorEventLoop):
	def __init__(self, console_app: bool = ..., *eventloop_args) -> None: ...
