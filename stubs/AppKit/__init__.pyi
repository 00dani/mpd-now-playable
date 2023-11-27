from typing import Final, Literal

from Foundation import CGSize

# There are many other operations available but we only actually use copy, so we don't need all of them here.
NSCompositingOperationClear: Final = 0
NSCompositingOperationCopy: Final = 1
NSCompositingOperation = Literal[0, 1]

class NSRect:
    pass

def NSMakeRect(x: float, y: float, w: float, h: float) -> NSRect: ...

class NSImage:
    @staticmethod
    def alloc() -> type[NSImage]: ...

    @staticmethod
    def initByReferencingFile_(file: str) -> NSImage: ...

    @staticmethod
    def initWithData_(data: bytes) -> NSImage: ...

    @staticmethod
    def initWithSize_(size: CGSize) -> NSImage: ...

    def size(self) -> CGSize: ...

    def lockFocus(self) -> None: ...
    def unlockFocus(self) -> None: ...

    def drawInRect_fromRect_operation_fraction_(self, inRect: NSRect, fromRect: NSRect, operation: NSCompositingOperation, fraction: float) -> None: ...
