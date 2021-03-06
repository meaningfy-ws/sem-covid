# SemCovid *services* module

This module is part of the SemCovid project and represents the implementation of the service layer as described in the [Clean Architecture with Python](https://www.cosmicpython.com/book/introduction.html) book. The separate modules cannot be considered as standalone components and have to be treated as functionally dependent parts of the whole.

The application services (layer), sometimes called an orchestration layer or a use-case layer; the primary job is to handle requests from outside and orchestrate operations. This shall not be confused with domain services which, in contrast to application services, do not depend on any persistence or stateful entity. The service layer together with API development is described in more detail [here](https://www.cosmicpython.com/book/chapter_04_service_layer.html).

In order to deploy and execute the project (for example the dataset creation DAGS), however, it is best to refer to the [sem-covid project readme file](https://github.com/meaningfy-ws/sem-covid) or the [sem-covid-infra readme file](https://github.com/meaningfy-ws/sem-covid-infra).