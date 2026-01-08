import sys
import tomllib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = BASE_DIR / "config.toml"


def validate_config(conf: dict) -> list[str]:
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