"""Generates architecture diagrams for the documentation site."""

from diagrams import Cluster, Diagram, Edge
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python

# The filename path places the output directly into the docs/architecture folder
with Diagram(
    "ArXiv Ingestion ETL Pipeline",
    show=False,
    direction="LR",
    filename="docs/architecture/etl_architecture",
):
    api = FastAPI("FastAPI Router")

    with Cluster("Prefect Orchestration"):
        orchestrator = Server("Prefect Flow")

        with Cluster("Prefect Background Worker"):
            extract = Python("ArXiv Fetcher")
            download = Python("PDF Downloader")
            transform = Python("Docling Parser")
            load = Python("Ingestion Service")

            extract >> download >> transform >> load

    arxiv_api = Server("ArXiv API")
    vision_models = Server("Vision Models")
    db = PostgreSQL("App DB")

    api >> Edge(label="Async Trigger", color="darkblue") >> orchestrator
    orchestrator >> Edge(label="Dispatches Task") >> extract

    extract >> Edge(label="HTTP 429 Retry Logic", color="red") >> arxiv_api
    transform >> Edge(label="PyTorch TableFormer", color="purple") >> vision_models
    load >> Edge(label="SQLAlchemy ORM") >> db
