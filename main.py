import sys
import tomllib
from colorthief import ColorThief
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


def GetConfig():
    with open("config.toml", "rb") as f:
        conf = tomllib.load(f)

    return conf


def VerifyArgs():
    if len(sys.argv) < 2:
        print("Usage: main.py <image>")
        exit(2)

    img_arg = sys.argv[1]
    img_path = Path(img_arg)
    if not img_path.exists():
        print("File does not exist")
        exit(1)

    return img_path


def GetColors(image: Path, quality, count: int):
    color_thief = ColorThief(image)
    dominant_rgb = color_thief.get_color(quality)
    palette = color_thief.get_palette(count, quality)
    return palette, dominant_rgb


def RenderTemplates(palette: list, template: str) -> str:
    templates = Environment(loader=FileSystemLoader("templates"))
    sway_template = templates.get_template(template)
    out = sway_template.render({"palette": palette})
    return out


def SaveTemplate(out_dir: Path, template: str):
    with open(out_dir, "w") as file:
        file.write(template)


def ConvertRGB(input: list[tuple]) -> list[str]:
    output = []
    for x in input:
        y = "#{:02X}{:02X}{:02X}".format(x[0], x[1], x[2])
        output.append(y)

    return output


conf = GetConfig()
color_conf = conf["colors"]
files_conf = conf["files"]

img_path = VerifyArgs()
colors = GetColors(img_path, color_conf["quality"], color_conf["count"])
hex_rgb = ConvertRGB(colors[0])

out_path = Path(files_conf["out_dir"])
out_path.mkdir(exist_ok=True)

for file in files_conf["templates"]:
    templates = RenderTemplates(hex_rgb, file)
    out_file = out_path / Path(file).stem
    SaveTemplate(out_file, templates)
