# SemCovid *DAG entrypoint* module

This module is part of the SemCovid project and represents the implementation of the service layer as described in the [Clean Architecture with Python](https://www.cosmicpython.com/book/introduction.html) book. The separate modules cannot be considered as standalone components and have to be treated as functionally dependent parts of the whole.

The entrypoints are places the application is driven from; a.k.a. primary/driving or outwards facing adapters. This is where we implement APIs, CLIs and UIs. In the SemCovid project case, we implement the data processing pipelines as entrypoint artefacts. The entrypoint layer is described in more detail [here][https://www.cosmicpython.com/book/chapter_04_service_layer.html].

In order to deploy and execute the project (for example the dataset creation DAGS), however, it is best to refer to the [sem-covid project readme file](https://github.com/meaningfy-ws/sem-covid) or the [sem-covid-infra readme file](https://github.com/meaningfy-ws/sem-covid-infra).