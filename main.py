import sys
import shutil
import tomllib
from colorthief import ColorThief
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
CONFIG_FILE = BASE_DIR / "config.toml"


def get_config() -> dict:
    with open(CONFIG_FILE, "rb") as f:
        conf = tomllib.load(f)

    return conf


def get_img_path() -> Path:
    if len(sys.argv) < 2:
        print("Usage: main.py <image>")
        sys.exit(2)

    img_path = Path(sys.argv[1])
    if not img_path.exists():
        print(f"Error: File does not exist: {img_path}")
        sys.exit(1)

    return img_path


def get_colors(image: Path, quality: int, count: int):
    thief = ColorThief(image)
    dominant = thief.get_color(quality)
    palette = thief.get_palette(color_count=count, quality=quality)
    return {
        "dominant": dominant,
        "palette": palette,
    }


def render_template(env: Environment, template: str, palette: list) -> str:
    j2_template = env.get_template(template)
    out = j2_template.render({"palette": palette})
    return out


def save_file(out_dir: Path, template: str):
    with open(out_dir, "w") as file:
        file.write(template)


def convert_to_rgb(input: list[tuple]) -> list[str]:
    output = []
    for x in input:
        y = "#{:02X}{:02X}{:02X}".format(x[0], x[1], x[2])
        output.append(y)

    return output


def main():
    conf = get_config()
    color_conf = conf["colors"]
    files_conf = conf["files"]

    img_path = get_img_path()
    colors = get_colors(img_path, color_conf["quality"], color_conf["count"])
    hex_rgb = convert_to_rgb(colors["palette"])

    out_path = Path(img_path.stem)
    out_path.mkdir(exist_ok=True)

    template_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    for template_name in files_conf["templates"]:
        templates = render_template(template_env, template_name, hex_rgb)
        out_file = out_path / Path(template_name).stem
        save_file(out_file, templates)

    if files_conf["final_dir"]:
        outfile = "wallpaper" + img_path.suffix
        shutil.copy2(img_path, out_path / outfile)
        shutil.copytree(
            out_path, files_conf["final_dir"] / out_path, dirs_exist_ok=True
        )


if __name__ == "__main__":
    main()
