# EU Cellar COVID-19 dataset (ds_eu_cellar)

The Cellar is the semantic repository of the Publications Office. It stores
important legal documents, general publications and other important EU level
documents. We query this repository in order to construct the EU level COVID-19
datasets containing the document content and the associated metadata.


You can download the dataset following [this link](ds_eu_cellar.zip) and [this link](ds_eu_cellar.z01).


## Detailed description
In the context of the current exercise, we distinguish the core and the
extended datasets variants which are results of querying Cellar with two
different SPARQL queries.

The core dataset is the result of querying for documents (called works) in the
Cellar, which are annotated with a special “COVID-19” tag. The tagging is
performed manually by the EurLex team and its contractors. This tag marks
documents that have been identified as dealing directly with issues of the
COVID-19 pandemic.

The extended dataset is also the result of querying for documents (called works)
in Cellar , which are annotated with any of the [EuroVoc](https://op.europa.eu/en/web/eu-vocabularies/dataset/-/resource?uri=http://publications.europa.eu/resource/dataset/eurovoc) concepts that have been
identified as relevant to COVID-19 pandemics. The list of selected EuroVoc
concepts is provided in Table 1.

| Concept URI | Concept preferred label |
| ----------- | ----------------------- |
| http://eurovoc.europa.eu/1005 | EU financing |
| http://eurovoc.europa.eu/1439 | innovation |
| http://eurovoc.europa.eu/1633 | free movement of persons|
| http://eurovoc.europa.eu/1754 | illness |
| http://eurovoc.europa.eu/1756 | respiratory disease |
| http://eurovoc.europa.eu/1759 | infectious disease |
| http://eurovoc.europa.eu/1802 | labour market |
| http://eurovoc.europa.eu/1854 | disease prevention |
| http://eurovoc.europa.eu/192  | health control |
| http://eurovoc.europa.eu/2916 | applied research |
| http://eurovoc.europa.eu/2923 | medical research |
| http://eurovoc.europa.eu/3730 | health risk |
| http://eurovoc.europa.eu/3885 | public health |
| http://eurovoc.europa.eu/4470 | tourism |
| http://eurovoc.europa.eu/4505 | air transport |
| http://eurovoc.europa.eu/5237 | research and development |
| http://eurovoc.europa.eu/835  | aid to undertakings |
| http://eurovoc.europa.eu/1280 | occupational health |
| http://eurovoc.europa.eu/1634 | free movement of workers |
| http://eurovoc.europa.eu/2062 | standard of living |
| http://eurovoc.europa.eu/2479 | health policy |
| http://eurovoc.europa.eu/5891 | public awareness campaign |
| http://eurovoc.europa.eu/82   | working conditions |
| http://eurovoc.europa.eu/2473 | communications policy |
| http://eurovoc.europa.eu/3086 | economic consequence |
| http://eurovoc.europa.eu/4636 | vaccination |
| http://eurovoc.europa.eu/5992 | economic activity |
| http://eurovoc.europa.eu/712  | economic support |
| http://eurovoc.europa.eu/826  | aid to disadvantaged groups |
| http://eurovoc.europa.eu/1596 | health legislation |
| http://eurovoc.europa.eu/2870 | quality of life |
| http://eurovoc.europa.eu/3956 | social sciences |
| http://eurovoc.europa.eu/899  | economic aid |
| http://eurovoc.europa.eu/7983 | European Centre for Disease Prevention and Control |
| http://eurovoc.europa.eu/83   | living conditions |
| http://eurovoc.europa.eu/85   | social situation |
| http://eurovoc.europa.eu/5764 | organisation of health care |
| http://eurovoc.europa.eu/3552 | teleworking |
| http://eurovoc.europa.eu/1742 | job preservation |
| http://eurovoc.europa.eu/886  | state of emergency |
| http://eurovoc.europa.eu/1926 | working environment |
| http://eurovoc.europa.eu/4116 | health service |
| http://eurovoc.europa.eu/5612 | protective equipment |
| http://eurovoc.europa.eu/837  | epidemic |
| http://eurovoc.europa.eu/2270 | social participation |
| http://eurovoc.europa.eu/838  | epidemiology |
| http://eurovoc.europa.eu/2793 | aid programme |
| http://eurovoc.europa.eu/3588 | restriction of liberty |
| http://eurovoc.europa.eu/6781 | basic needs |
| http://eurovoc.europa.eu/3371 | public hygiene |
| http://eurovoc.europa.eu/2013 | mass media |
| http://eurovoc.europa.eu/7131 | social impact |
| http://eurovoc.europa.eu/3906 | freedom of movement |
| http://eurovoc.europa.eu/3370 | patient rights |
| http://eurovoc.europa.eu/4881 | social well-being |
| http://eurovoc.europa.eu/86   | socioeconomic conditions |
| http://eurovoc.europa.eu/1758 | endemic disease |
| http://eurovoc.europa.eu/779  | distance learning |
| http://eurovoc.europa.eu/6609 | self-regulation |
| http://eurovoc.europa.eu/6770 | disinformation |
| http://eurovoc.europa.eu/c_324b44f1 | social media |
| http://eurovoc.europa.eu/c_5b447e3a | crisis management |
| http://eurovoc.europa.eu/c_31da5694 | e-Health |
| http://eurovoc.europa.eu/c_60d3928d | patient safety |
| http://eurovoc.europa.eu/c_9b88f778 | hospital infection |
| http://eurovoc.europa.eu/c_ece0a719 | viral disease |
| http://eurovoc.europa.eu/c_814bb9e4 | coronavirus disease |
| http://eurovoc.europa.eu/c_abfaf2ea | disease surveillance |

Table 1: EuroVoc concepts considered highly relevant for COVID-19 document search


The result of querying Cellar in both cases (core and extended datasets) contains
the same data attributes. The difference is in the retrieved documents.
The structure of the eu_cellar dataset is provided in Table 2.

| Data attributes | Description |
| ----------------|-------------|
| Work URI        | The URI that uniquely identifies the work in Cellar. |
| CDM type        | The work type according to the Common Data Model ontology. |
| Resource type   | The work type according to the OP classification used in the European inter-     institutional exchange of legal documents. The resource types are organised in a classification scheme called Resource Type.
| EuroVoc concept | The EuroVoc concept used as topic and classifier of the document content. The  EuroVoc thesaurus is developed by the OP and used in the inter-institutional context. The concepts are organised as taxonomies from the broad to more narrow concepts.
| Subject matter  | The subject matter concept used as topic and classifier of the document content. The Subject Matter controlled vocabulary is developed by the OP and used in the inter-institutional context. The concepts are organised in a classification scheme called subject-matter, or FD_070.
| Directory code  | The directory code concept used to organise the legal documents in the EurLEx website. The concepts are organised in a classification scheme called FD_555.
| Author          | The authors of the legal document. The identifier of the authors provided here is from the controlled list called Corporate Body.
| Date document   | The date document was issued, entered into force, signed or other date relevant for the document legality.
| Content         | The actual content of the legal document, reduced to simple unstructured text.
| Title           | The document tile.

Table 2: The attribute structure for eu_cellar dataset


Finally the core and the extended dataset variants are merged and provided as a
unified EU Cellar COVID-19 dataset.

# Contributing

You are more than welcome to help expand and mature this project.

When contributing to this repository, please first discuss the change you wish
to make via GitHub issues with the owners of this repository before making a change.

Please note we adhere to [Apache code of conduct](https://www.apache.org/foundation/policies/conduct), please follow it in all your interactions with the project.

# License

The documents, such as reports and specifications, available in the /doc folder,
are licenced under a [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/deed.en).

The scripts (stylesheets) and other executables are licenced under [EUPL-1.2](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12) licence.
