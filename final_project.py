from fastapi import FastAPI
from urllib3 import HTTPResponse
from nbconvert import HTMLExporter
import nbformat

app = FastAPI()

@app.get("/{ITMD_522_Project}")
async def read_notebook(ITMD_522_Project: str):
    # Modify the path to the Jupyter Notebook file
    notebook_path = "C:/Users/91996/Documents/Fall_22-DM-ML/Project/ITMD_522_Project.ipynb" + ITMD_522_Project + ".ipynb"

    # Open the Jupyter Notebook file
    with open(notebook_path, "r", encoding="utf-8") as nb_file:
        nb_contents = nb_file.read()

    # Convert the notebook to HTML format
    nb_node = nbformat.reads(nb_contents, as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.exclude_input_prompt = True
    html_exporter.exclude_output_prompt = True
    (body, _) = html_exporter.from_notebook_node(nb_node)

    # Serve the HTML file using FastAPI
    return HTTPResponse(content=body, status_code=200)
