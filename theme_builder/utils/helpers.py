import sys
import shutil
import argparse
from pathlib import Path


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


def check_disk_space(output_path: Path, estimated_size_mb: int = 10) -> None:
    """Check available disk space."""
    try:
        stat = shutil.disk_usage(output_path.parent)
        available_mb = stat.free // (1024 * 1024)
        
        if available_mb < estimated_size_mb:
            raise OSError(f"Insufficient disk space: {available_mb}MB available, {estimated_size_mb}MB required")
    except OSError as e:
        sys.exit(f"Error checking disk space: {e}")


def save_file(output_path: Path, content: str) -> None:
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


def copy_with_error_handling(src: Path, dst: Path) -> None:
    """Copy file with error handling."""
    try:
        shutil.copy2(src, dst)
    except PermissionError:
        sys.exit(f"Error: Permission denied copying {src} to {dst}")
    except OSError as e:
        sys.exit(f"Error copying file: {e}")