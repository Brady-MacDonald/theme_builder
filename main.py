import shutil
import sys
import tomllib
import argparse
import os
from pathlib import Path

# Validate dependencies at import time
try:
    from colorthief import ColorThief
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError, UndefinedError
except ImportError as e:
    sys.exit(f"Error: Missing required dependency: {e}\n"
             f"Install with: pip install -r requirements.txt")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
CONFIG_FILE = BASE_DIR / "config.toml"


def validate_config(conf: dict):
    """Validate configuration values and structure."""
    errors = []
    
    # Validate colors section
    if "colors" not in conf:
        errors.append("Missing required [colors] section in config.toml")
    else:
        colors = conf["colors"]
        required_color_fields = ["quality", "count"]
        
        for field in required_color_fields:
            if field not in colors:
                errors.append(f"Missing required 'colors.{field}' in config.toml")
        
        # Validate color count
        if "count" in colors:
            if not isinstance(colors["count"], int) or colors["count"] <= 0:
                errors.append("Color count must be a positive integer")
            elif colors["count"] > 20:  # Reasonable limit
                errors.append("Color count too large (max: 20)")
        
        # Validate quality
        if "quality" in colors:
            if not isinstance(colors["quality"], int) or colors["quality"] < 1:
                errors.append("Quality must be a positive integer")
    
    # Validate files section
    if "files" not in conf:
        errors.append("Missing required [files] section in config.toml")
    else:
        files = conf["files"]
        
        if "templates" not in files:
            errors.append("Missing required 'files.templates' in config.toml")
        elif not isinstance(files["templates"], list) or not files["templates"]:
            errors.append("Templates list cannot be empty")
        
        # Check final directory if specified
        if "final_dir" in files and files["final_dir"]:
            final_dir = Path(files["final_dir"])
            if not final_dir.exists():
                try:
                    final_dir.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    errors.append(f"Cannot create final directory: {final_dir}")
    
    return errors


def get_config() -> dict:
    """Load and validate configuration file."""
    try:
        if not CONFIG_FILE.exists():
            raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE}")
        
        conf = tomllib.loads(CONFIG_FILE.read_text())
        
        # Validate configuration
        errors = validate_config(conf)
        if errors:
            sys.exit("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return conf
        
    except FileNotFoundError as e:
        sys.exit(f"Error: {e}")
    except tomllib.TOMLDecodeError as e:
        sys.exit(f"Error: Invalid TOML in config file: {e}")
    except PermissionError:
        sys.exit(f"Error: Permission denied reading config file: {CONFIG_FILE}")
    except Exception as e:
        sys.exit(f"Error loading configuration: {e}")


def validate_alpha(value: str) -> float:
    """Validate alpha argument is between 0 and 1."""
    try:
        alpha = float(value)
        if not 0.0 <= alpha <= 1.0:
            raise argparse.ArgumentTypeError(f"Alpha value must be between 0.0 and 1.0, got {alpha}")
        return alpha
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid alpha value: {value}")


def parse_args():
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate theme files from an image's color palette."
    )

    # Positional image file
    parser.add_argument("image", type=Path, help="Path to the input image")

    # Optional arguments
    parser.add_argument(
        "--alpha",
        "-a",
        type=validate_alpha,
        default=1.0,
        help="Alpha value for RGBA colors (0.0-1.0, default: 1.0)",
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

    args = parser.parse_args()
    
    # Additional validation
    if not args.image:
        parser.error("Image file path is required")
    
    return args


def get_colors(image: Path, quality: int, count: int):
    """Extract color palette from image with comprehensive error handling."""
    try:
        # Validate image file exists and is readable
        if not image.exists():
            raise FileNotFoundError(f"Image file not found: {image}")
        
        if not image.is_file():
            raise ValueError(f"Path is not a file: {image}")
        
        # Check file extension for supported formats
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        if image.suffix.lower() not in supported_formats:
            raise ValueError(f"Unsupported image format: {image.suffix} "
                           f"(supported: {', '.join(sorted(supported_formats))})")
        
        print(f"[+] Extracting colors from image: {image}")
        print(f"    → quality={quality}, count={count}")
        
        thief = ColorThief(str(image))  # Convert to string for ColorThief
        palette = thief.get_palette(color_count=count, quality=quality)
        
        if not palette:
            raise ValueError("Color extraction failed - no colors found in image")
        
        print("[✓] Color extraction complete")
        return {"palette": palette}
        
    except FileNotFoundError as e:
        sys.exit(f"Error: {e}")
    except ValueError as e:
        sys.exit(f"Error: {e}")
    except Exception as e:
        sys.exit(f"Error processing image {image}: {e}")


def convert_to_hex(input_list: list[tuple]) -> list[str]:
    """Convert RGB tuples to hex strings with validation."""
    if not input_list:
        raise ValueError("Color palette is empty")
    
    output = []
    for i, rgb in enumerate(input_list):
        if not isinstance(rgb, (list, tuple)) or len(rgb) != 3:
            raise ValueError(f"Invalid RGB value at index {i}: {rgb}")
        
        r, g, b = rgb
        if not all(isinstance(val, int) and 0 <= val <= 255 for val in [r, g, b]):
            raise ValueError(f"RGB values must be integers 0-255 at index {i}: {rgb}")
        
        hex_val = "#{:02X}{:02X}{:02X}".format(r, g, b)
        output.append(hex_val)
    
    return output


def convert_to_rgba(rgb_list: list[tuple], alpha: float) -> list[str]:
    """Convert RGB tuples to RGBA strings with validation."""
    if not rgb_list:
        raise ValueError("Color palette is empty")
    
    a = int(alpha * 255)
    if not (0 <= a <= 255):
        raise ValueError(f"Invalid alpha value: {alpha}")
    
    rgba_list = []
    for i, (r, g, b) in enumerate(rgb_list):
        if not all(isinstance(val, int) and 0 <= val <= 255 for val in [r, g, b]):
            raise ValueError(f"RGB values must be integers 0-255 at index {i}: {(r, g, b)}")
        rgba_list.append(f"#{r:02X}{g:02X}{b:02X}{a:02X}")
    
    return rgba_list


def print_palette_colors(hex_palette: list[str]):
    print("\nPalette Preview:")
    for hx in hex_palette:
        r = int(hx[1:3], 16)
        g = int(hx[3:5], 16)
        b = int(hx[5:7], 16)
        print(f"\x1b[48;2;{r};{g};{b}m  \x1b[0m {hx}")
    print()


def check_disk_space(output_path: Path, estimated_size_mb: int = 10):
    """Check available disk space."""
    try:
        stat = shutil.disk_usage(output_path.parent)
        available_mb = stat.free // (1024 * 1024)
        
        if available_mb < estimated_size_mb:
            raise OSError(f"Insufficient disk space: {available_mb}MB available, {estimated_size_mb}MB required")
    except OSError as e:
        sys.exit(f"Error checking disk space: {e}")


def render_template(env: Environment, template: str, colors: dict) -> str:
    """Render template with comprehensive error handling."""
    try:
        j2_template = env.get_template(template)
        return j2_template.render(palette=colors["hex"], rgba=colors["rgba"])
    except TemplateNotFound:
        sys.exit(f"Error: Template file not found: {template}")
    except TemplateSyntaxError as e:
        sys.exit(f"Error: Template syntax error in {template} at line {e.lineno}: {e.message}")
    except UndefinedError as e:
        sys.exit(f"Error: Template variable error in {template}: {e}")
    except Exception as e:
        sys.exit(f"Error rendering template {template}: {e}")


def save_file(output_path: Path, content: str):
    """Save file with proper error handling."""
    try:
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding='utf-8') as file:
            file.write(content)
    except PermissionError:
        sys.exit(f"Error: Permission denied writing to: {output_path}")
    except OSError as e:
        sys.exit(f"Error: Failed to write file {output_path}: {e}")


def copy_with_error_handling(src: Path, dst: Path):
    """Copy file with error handling."""
    try:
        shutil.copy2(src, dst)
    except PermissionError:
        sys.exit(f"Error: Permission denied copying {src} to {dst}")
    except OSError as e:
        sys.exit(f"Error copying file: {e}")


def main():
    """Main function with comprehensive error handling."""
    try:
        # Load and validate configuration
        conf = get_config()
        color_conf = conf["colors"]
        files_conf = conf["files"]

        # Parse and validate command line arguments
        args = parse_args()
        img_path = args.image
        
        if not img_path.exists():
            sys.exit(f"Error: Image file not found: {img_path}")
        
        print(f"Processing image: {img_path}")

        # Extract colors with validation
        colors = get_colors(img_path, color_conf["quality"], color_conf["count"])
        
        # Convert colors with validation
        try:
            colors["hex"] = convert_to_hex(colors["palette"])
            colors["rgba"] = convert_to_rgba(colors["palette"], args.alpha)
        except ValueError as e:
            sys.exit(f"Error in color conversion: {e}")

        # Print palette preview
        print_palette_colors(colors["hex"])

        # Create output directory
        out_path = Path(img_path.stem)
        try:
            out_path.mkdir(exist_ok=True)
        except PermissionError:
            sys.exit(f"Error: Permission denied creating output directory: {out_path}")
        except OSError as e:
            sys.exit(f"Error creating output directory: {e}")

        # Check disk space
        check_disk_space(out_path)

        # Validate template directory
        if not TEMPLATE_DIR.exists():
            sys.exit(f"Error: Template directory not found: {TEMPLATE_DIR}")

        # Setup Jinja2 environment
        template_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

        # Process templates
        for template_name in files_conf["templates"]:
            try:
                template_content = render_template(template_env, template_name, colors)
                template_stem = Path(template_name).name
                output_file = out_path / template_stem
                save_file(output_file, template_content)
                
                if args.verbose:
                    print(f"[✓] Generated: {output_file}")
                    
            except Exception as e:
                sys.exit(f"Error processing template {template_name}: {e}")

        # Copy to final directory if configured
        if files_conf["final_dir"]:
            try:
                outfile = "wallpaper" + img_path.suffix
                output_wallpaper = out_path / outfile
                
                copy_with_error_handling(img_path, output_wallpaper)
                
                final_dir = Path(files_conf["final_dir"]) / out_path
                shutil.copytree(out_path, final_dir, dirs_exist_ok=True)
                
                if args.verbose:
                    print(f"[✓] Theme copied to: {final_dir}")
                    
            except Exception as e:
                sys.exit(f"Error copying theme files: {e}")

        if args.verbose:
            print("[✓] Theme generation complete.")
            
    except KeyboardInterrupt:
        sys.exit("\nError: Theme generation interrupted by user")
    except Exception as e:
        sys.exit(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
