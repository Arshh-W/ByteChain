"""Image analysis utilities used by the ByteChain verification endpoint."""

from PIL import Image, ImageStat


SUPPORTED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP", "BMP", "GIF", "TIFF"}


def analyze_image(file_path: str) -> tuple[float, bool]:
	"""Validate an image and run a deterministic forensic baseline."""
	with Image.open(file_path) as image:
		if image.format not in SUPPORTED_IMAGE_FORMATS:
			raise ValueError("Unsupported image format")
		image.verify()

	with Image.open(file_path) as image:
		grayscale = image.convert("L")
		width, height = grayscale.size
		if width < 32 or height < 32:
			raise ValueError("Image must be at least 32x32 pixels")
		standard_deviation = ImageStat.Stat(grayscale).stddev[0]

	quality_penalty = 0.0
	if standard_deviation < 8:
		quality_penalty += 0.18
	if min(width, height) < 128:
		quality_penalty += 0.12

	confidence_score = round(max(0.05, min(0.99, 0.98 - quality_penalty)), 4)
	is_tampered = quality_penalty >= 0.25
	return confidence_score, is_tampered
