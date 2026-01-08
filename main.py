import sys
import shutil
from pathlib import Path

from theme_builder.config.manager import get_config
from theme_builder.colors.extractor import extract_colors, convert_to_hex, convert_to_rgba, print_palette_colors
from theme_builder.templates.renderer import create_template_environment, render_template
from theme_builder.utils.helpers import parse_args, check_disk_space, save_file, copy_with_error_handling


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
        colors = extract_colors(img_path, color_conf["quality"], color_conf["count"])
        
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

        # Setup Jinja2 environment
        template_env = create_template_environment()

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