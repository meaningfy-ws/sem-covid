# Policy watch database (ds_pwdb)
Policy Watch Database (PWDB) is a suitable set of summarised descriptions of
what a COVID-19 measure looks like. They cover broader context economic and
social issues and intentionally exclude COVID-19 reactions, which focus mostly
on the public health related issues.

You can download the dataset following [this link](ds_pwdb.zip).

## Detailed description
Eurofound's COVID-19 EU PolicyWatch (PWDB) collates information on the responses
of EU Member States and their social partners to the crisis in the domain of living and working conditions. It also gathers examples of
company practices aimed at mitigating the social and economic impacts. Data has
been mainly provided by the Eurofound's national correspondents network, with quality
control carried out by Eurofound staff.
PWDB includes large-scale government measures and wider collective agreements,
as well as regional and local initiatives and support measures for smaller
groups of workers. As the situation is evolving, measures are newly implemented,
changed or cancelled and replaced at rapid speed. It is planned to update the
cases with information on the actual uptake of the main measures. 

The original PWDB contains a rich set of attributes. Only a subset is considered
relevant from the business perspective to the current project and is listed in
the table below. The original structure is transformed into a simplified form
for harmonisation with other datasets and easier usage. The data structure of
the transformed core PWDB dataset (ds_pwdb_core) is described in Table 1 and



| Data attribute    | Description |
| ----------------- | ----------- |
| Category | Nine high-level categories for grouping the COVID-19 measures  (proposed by the EuroFond team).
| Subcategory | Further categorisation into fine grained categories, under a parent category. The two level taxonomy is not documented here but can be recreated from the dataset.  |
| Target group (L1) | The database provides target groups for each measure. Target groups are organised on two levels: L1 & L2. The L1 level broadly differentiates between workers, businesses and citizens.
| Target group (L2) | The L2 level contains more fine-grained distinctions containing 42 specific target groups distinctions in total, including for example:  1. Workers: Self-employed, Seasonal workers, Platform workers, etc. 2. Businesses: SMEs, Start-ups, Larger corporations, etc. 3. Citizens: Parents, Older citizens, Migrants, etc.
| Country | The country where the COVID-19 measure is adopted by the government and social partners.
| Involved actors | Eurofound identified 757 legislations and other statutory regulations, 452 of which have been created entirely in the context of COVID-19. This section gives an overview of social partner's involvement in designing and implementing these measures.
| Funding | The sources of financing the measure, if the measure involves financial expenditures. Some measures do not require any fundings.
| Type | Classification of the document types from where the measures description originates. Six types of source documents are distinguished, including legislations, collective agreements, recommendations and company practices.
| Start & End dates | The time period when the measure is applied.
| Creation date  | When the measure entry was created in the database
| Update date  | When last changes were made to the measure entry description.
| Background information | A short text providing the context and background information useful to understand the measure description.
| Content of measure | A short text representing the abstract or a very short description of the measure.
| Content updates | Short updates to the content of measure.
| Use of measure | Information about the results and outcomes of executing/enacting the measure.
| Title | A short text used to identify the measure, to place it in context and to convey a minimal summary of its contents.

Table 1: The attribute structure for core PWDB dataset (ds_pwdb_core)


In the core dataset, a list of source references is provided. They represent
links to the original documents elaborating on the contents of the measure.
 We proceeded with downloading, cleaning and injecting the content of the
 original sources into the PWD dataset, this way extending it.

In the extended version of the PWDB dataset, an additional set of data
attributes is provided as is listed in Table 2.


| Data attribute | Description |
| -------------- | ----------- |
| Source URL | The measure descriptions are based on external sources referenced by URLs
| Source content | The content (in plain text) downloaded by accessing the document at the source URL.
| Source title | The title of the source document, if possible to retrieve
| Source language | The language of the source content is determined by a language identification system.

Table 2: The additional set of attributes constituting the PWBD extension (ds_pwdb_ext)


Finally the core and the extended dataset variants are merged and provided as a
unified PWDB dataset.

# Contributing

You are more than welcome to help expand and mature this project.

When contributing to this repository, please first discuss the change you wish
to make via GitHub issues with the owners of this repository before making a change.

Please note we adhere to [Apache code of conduct](https://www.apache.org/foundation/policies/conduct), please follow it in all your interactions with the project.

# License

The documents, such as reports and specifications, available in the /doc folder,
are licenced under a [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/deed.en).

The scripts (stylesheets) and other executables are licenced under [EUPL-1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) licence.
