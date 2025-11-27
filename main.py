import os
from typing import Union
import sys
from pathlib import Path

from colorthief import ColorThief
from jinja2 import Environment, FileSystemLoader

PathLike = Union[str, Path]

if len(sys.argv) < 2:
    print("Usage: main.py <image>")
    exit(2)


def GetColors(image: str):
    color_thief = ColorThief(image)
    dominant_color = color_thief.get_color()
    palette = color_thief.get_palette(color_count=5)
    return palette, dominant_color


def RenderTemplates(palette: list) -> str:
    templates = Environment(loader=FileSystemLoader("templates"))
    sway_template = templates.get_template("swaync.css.j2")
    out = sway_template.render({"palette": palette})
    return out


def SaveTemplate(output, template: str):
    with open(output, "w") as file:
        file.write(template)


def SymLink(src: PathLike, dst: PathLike):
    os.symlink("", "", target_is_directory=True)


output_location = "output"
img = sys.argv[1]

out_path = Path(output_location)
out_path.mkdir(exist_ok=True)

color_pallete = GetColors(img)
templates = RenderTemplates(color_pallete)
SaveTemplate()

SymLink(out_path, 123)


img_path = Path(img)
img_name = img_path.stem
