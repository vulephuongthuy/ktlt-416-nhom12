from pathlib import Path
from PIL import Image, ImageDraw, ImageTk

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets" / "frame0"
PROFILE_PIC_PATH = OUTPUT_PATH / "profile_pictures"

# Đảm bảo thư mục lưu ảnh tồn tại
PROFILE_PIC_PATH.mkdir(parents=True, exist_ok=True)

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def reduce_opacity(image, opacity=1.0):
    if image.mode != "RGBA": image = image.convert("RGBA")  # Đảm bảo ảnh có kênh Alpha
    alpha = image.split()[3]  # Lấy kênh Alpha
    alpha = alpha.point(lambda p: int(p * opacity))  # Điều chỉnh độ trong suốt
    image.putalpha(alpha)
    return image  # Trả về ảnh đã chỉnh sửa


def round_corners(image, radius):
    rounded = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius=radius, fill=255)
    rounded.paste(image, (0, 0), mask)
    return rounded

