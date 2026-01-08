import sys
from pathlib import Path

# Validate dependencies at import time
try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError, UndefinedError
except ImportError as e:
    sys.exit(f"Error: Missing required dependency: {e}\n"
             f"Install with: pip install -r requirements.txt")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"


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


def create_template_environment() -> Environment:
    """Create and return a Jinja2 template environment."""
    if not TEMPLATE_DIR.exists():
        sys.exit(f"Error: Template directory not found: {TEMPLATE_DIR}")
    
    return Environment(loader=FileSystemLoader(TEMPLATE_DIR))