
import os
import pathlib


def convert_notebook_to_html(notebook_path: pathlib.Path, published_html_path: pathlib.Path) -> os.system:
    """
    This function allows us to publish jupyter notebooks in html extension
    """
    return os.system(f"jupyter nbconvert --output-dir={published_html_path} --to html {notebook_path}")
