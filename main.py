import shutil
import sys
import tomllib
import argparse
from pathlib import Path
from colorthief import ColorThief
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
CONFIG_FILE = BASE_DIR / "config.toml"


def get_config() -> dict:
    conf = tomllib.loads(CONFIG_FILE.read_text())
    return conf


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate theme files from an image's color palette."
    )

    # Positional image file
    parser.add_argument("image", type=Path, help="Path to the input image")

    # Optional arguments
    parser.add_argument(
        "--alpha",
        "-a",
        type=float,
        default=1.0,
        help="Alpha value for RGBA colors (default: 1.0)",
    )

    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        help="Print the generated color palette to the terminal",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose terminal output"
    )

    return parser.parse_args()


def get_colors(image: Path, quality: int, count: int):
    print(f"[+] Extracting colors from image: {image}")
    print(f"    → quality={quality}, count={count}")

    thief = ColorThief(image)
    palette = thief.get_palette(color_count=count, quality=quality)

    print("[✓] Color extraction complete")
    return {
        "palette": palette,
    }


def convert_to_hex(input: list[tuple]) -> list[str]:
    output = []
    for rgb in input:
        hex_val = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
        output.append(hex_val)

    return output


def convert_to_rgba(rgb_list: list[tuple], alpha: float) -> list[str]:
    a = int(alpha * 255)
    return [f"#{r:02X}{g:02X}{b:02X}{a:02X}" for r, g, b in rgb_list]


def print_palette_colors(hex_palette: list[str]):
    print("\nPalette Preview:")
    for hx in hex_palette:
        r = int(hx[1:3], 16)
        g = int(hx[3:5], 16)
        b = int(hx[5:7], 16)
        print(f"\x1b[48;2;{r};{g};{b}m  \x1b[0m {hx}")
    print()


def render_template(env: Environment, template: str, colors: dict) -> str:
    j2_template = env.get_template(template)
    out = j2_template.render(palette=colors["hex"], rgba=colors["rgba"])
    return out


def save_file(out_dir: Path, template: str):
    with open(out_dir, "w") as file:
        file.write(template)


def main():
    conf = get_config()
    color_conf = conf["colors"]
    files_conf = conf["files"]

    args = parse_args()
    img_path = args.image
    print(img_path)

    colors = get_colors(img_path, color_conf["quality"], color_conf["count"])
    colors["hex"] = convert_to_hex(colors["palette"])
    colors["rgba"] = convert_to_rgba(colors["palette"], args.alpha)

    print_palette_colors(colors["hex"])

    out_path = Path(img_path.stem)
    out_path.mkdir(exist_ok=True)

    template_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    for template_name in files_conf["templates"]:
        templates = render_template(template_env, template_name, colors)

        template_stem = Path(template_name).name
        out_file = out_path / template_stem

        save_file(out_file, templates)

    if files_conf["final_dir"]:
        outfile = "wallpaper" + img_path.suffix
        shutil.copy2(img_path, out_path / outfile)
        shutil.copytree(
            out_path, files_conf["final_dir"] / out_path, dirs_exist_ok=True
        )

    if args.verbose:
        print("[✓] Theme generation complete.")


if __name__ == "__main__":
    main()
