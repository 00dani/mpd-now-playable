from pathlib import Path

from AppKit import NSCompositingOperationCopy, NSImage, NSMakeRect
from Foundation import CGSize
from MediaPlayer import MPMediaItemArtwork


def logo_to_ns_image() -> NSImage:
	return NSImage.alloc().initByReferencingFile_(
		str(Path(__file__).parents[3] / "mpd/logo.svg")
	)


def data_to_ns_image(data: bytes) -> NSImage:
	return NSImage.alloc().initWithData_(data)


def data_to_media_item_artwork(data: bytes) -> MPMediaItemArtwork:
	return ns_image_to_media_item_artwork(data_to_ns_image(data))


def ns_image_to_media_item_artwork(img: NSImage) -> MPMediaItemArtwork:
	def resize(size: CGSize) -> NSImage:
		new = NSImage.alloc().initWithSize_(size)
		new.lockFocus()
		img.drawInRect_fromRect_operation_fraction_(
			NSMakeRect(0, 0, size.width, size.height),
			NSMakeRect(0, 0, img.size().width, img.size().height),
			NSCompositingOperationCopy,
			1.0,
		)
		new.unlockFocus()
		return new

	return MPMediaItemArtwork.alloc().initWithBoundsSize_requestHandler_(
		img.size(), resize
	)


MPD_LOGO = ns_image_to_media_item_artwork(logo_to_ns_image())
