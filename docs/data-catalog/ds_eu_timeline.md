# EU action timeline dataset (ds_eu_timeline)
The European Commission (EC) is coordinating a common European response  to the
coronavirus outbreak. EC is taking resolute action to reinforce our public health
sectors and mitigate the socio-economic impact in the European Union. EC is
mobilising means to help the Member States coordinate their national responses
and are providing objective information about the spread of the virus and
effective efforts to contain it.


You can download the dataset following [this link](http://srv.meaningfy.ws:9000/tmp-elasticsearch-dump/ds_eu_timeline.json?Content-Disposition=attachment%3B%20filename%3D%22ds_eu_timeline.json%22&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=2zVld17bTfKk8iu0Eh9H74MywAeDV3WQ%2F20210505%2F%2Fs3%2Faws4_request&X-Amz-Date=20210505T073902Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=9f565bcf5cc0790c14ced2ced348864c75cd60a07fcb7f7c3d40792c16990959).


## Detailed description
The European Commission (EC) is coordinating a common European response  to the
coronavirus outbreak. EC is taking resolute action to reinforce our public health
sectors and mitigate the socio-economic impact in the European Union. EC is
mobilising means to help the Member States coordinate their national responses
and are providing objective information about the spread of the virus and
effective efforts to contain it.

The timeline of EU actions during the COVID19 pandemics is a website published by
the EC with the most important COVID19 reponses. From 1104 actions (counted on 19/04/2021)
published in the press corner only 171 were mentioned on the EU action timeline.
So teh timeline constitutes a refinement of the noteworthy and an aggregation
of the EU actions.

We crawl this website and its content is automatically organised using the
attributes listed in Table 1. Unfortunately in the crawled content only a very
limited set of metadata can be identified: title, abstract, date of publication
and the actual content. And we know that the more metadata about a document,
the better it is for attempting to answer some of the questions mentioned in the
project goals section.

Following a discussion with the representatives of Directorate-General for
Communication (DG COMM), we identified a way to recover the possible topics
using the name(s) of the authors for each article. This is possible because
each author (spokesperson or press officer) is responsible for one or few topics.
These topics are assigned to each press contact who are on the spokesperson’s
service page.

What we did, was to first extract and structure the information about each person
 and the topics he/she covers. Then we extended the original crawler to take into
 consideration this mapping between the person name and the topics. A new data
 attribute is created for each article containing the array of possible topics
 that characterise the article.
Note that the list shall not be read as a conjunction, that is: the article is
about all of the topics provided; but as a disjunction, which means: the article
is about one of the provided topics.


| Data attribute | Description
| -------------- | -----------
| abstract       | A short summary of the article, an abstract.
| Content        | An extended description of the action as a press release article.
| Date           | The date when the press release was published
| Title          | The title of the press release article.
| Topic          | A list of possible topics that the article may be about, derived from  the author's thematic responsibility.

Table 1: The attribute structure for ds_eu_timeline

# Contributing

You are more than welcome to help expand and mature this project.

When contributing to this repository, please first discuss the change you wish
to make via issue, email, or any other method with the owners of this repository
before making a change.

Please note we adhere to [Apache code of conduct](https://www.apache.org/foundation/policies/conduct), please follow it in all your
interactions with the project.

# License

The documents, such as reports and specifications, available in the /doc folder,
are licenced under a [CC BY 4.0 licence](https://creativecommons.org/licenses/by/4.0/deed.en).

The scripts (stylesheets) and other executables are licenced under [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) licence.
