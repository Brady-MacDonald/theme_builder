# Theme Builder

For detailed information and examples, visit the [project page](https://bradymacdonald.com/projects/theme-builder).
A Python CLI tool that extracts color palettes from images and generates themed configuration files for Linux desktop environments (Hyprland, SwayNC, Waybar).

## Features

- Extract color palettes from images using ColorThief
- Generate themed configuration files from Jinja2 templates
- Support for multiple output formats (hex, RGBA)
- Built-in configuration validation and error handling
- Terminal color palette preview

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
# Basic usage
python main.py path/to/image.jpg

# With options
python main.py path/to/image.jpg --alpha 0.8 --preview --verbose
```

## Configuration

Edit `config.toml` to customize:
- Color extraction settings (quality, count)
- Template files to generate
- Output directory paths

## Project Structure

```
theme_builder/
├── main.py                # Main application entry point
├── config.toml            # Configuration file
├── requirements.txt       # Dependencies
├── templates/             # Jinja2 templates
└── theme_builder/         # Python package
    ├── config/            # Configuration management
    ├── colors/            # Color extraction/conversion
    ├── templates/         # Template rendering
    └── utils/             # File operations & CLI
```

