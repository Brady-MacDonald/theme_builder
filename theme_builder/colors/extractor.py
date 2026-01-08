import sys
from pathlib import Path

# Validate dependencies at import time
try:
    from colorthief import ColorThief
except ImportError as e:
    sys.exit(f"Error: Missing required dependency: {e}\n"
             f"Install with: pip install -r requirements.txt")


def extract_colors(image: Path, quality: int, count: int) -> dict:
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


def print_palette_colors(hex_palette: list[str]) -> None:
    """Print color palette preview to terminal."""
    print("\nPalette Preview:")
    for hx in hex_palette:
        r = int(hx[1:3], 16)
        g = int(hx[3:5], 16)
        b = int(hx[5:7], 16)
        print(f"\x1b[48;2;{r};{g};{b}m  \x1b[0m {hx}")
    print()