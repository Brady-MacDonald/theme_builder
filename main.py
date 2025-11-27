import sys
from pathlib import Path

from colorthief import ColorThief
from jinja2 import Environment, FileSystemLoader

output_location = "output"
if len(sys.argv) < 2:
    print("Usage: main.py <image>")
    exit(2)


def GetColors(image: str):
    color_thief = ColorThief(image)
    dominant_color = color_thief.get_color()
    palette = color_thief.get_palette(color_count=5)
    return palette, dominant_color


def Tester():
    x = Environment(loader=FileSystemLoader("templates"))
    template = x.get_template("tester.j2")
    out = template.render({"test": "brady"})
    print(out)


img = sys.argv[1]
color_pallete = GetColors(img)
print(color_pallete[0][0])

out_path = Path(output_location)
out_path.mkdir(exist_ok=True)

img_path = Path(img)
img_name = img_path.stem

# Tester()
