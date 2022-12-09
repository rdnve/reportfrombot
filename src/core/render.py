from jinja2 import Template

from core.settings import BASE_DIR


def render_to_string(filename: str, **kwargs) -> str:
    """
    Just render template to string w/ any kwargs.
    """
    with open(f"{BASE_DIR}/templates/{filename}", "r") as file:
        template = Template(file.read())
        return template.render(**kwargs)
