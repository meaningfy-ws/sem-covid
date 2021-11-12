# *WP3.5[BONUS] -Topic model explorer application*

## **Topic model explorer**

It is an application to visualize the topics in two dimentsional space and their comprising words along with frequenceies and relevancy.

## **How to use**

The application provides the possibility to choose a topic model for each of the sub-datasets of the Euro-Covid-19 dataset, namely: ds_pwdb, ds_eurlex, ds_eu_timeline, and ds_irish_timeline. 

In addition, the user may choose the topic model built on top of all language words or on a subset of words as follows:
- words: all the words in the corpus
- verbs: only the words that were recognised to be verbs
- nouns: only the words that were recognised to be nouns
- noun_phrases: the nouns and the noun phrases (including modifying adjectives)

After choosing the two options above and pressing the button 'Generate' a graphic is generated using the pyLDAVis library. Instructions on how to read and interpret the topic model visualisation are found in [the original paper](https://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf). 


## **How access the application?**
This web application can be accessed [here](http://srv.meaningfy.ws:8502/).

[**Source code**](
https://github.com/meaningfy-ws/sem-covid/blob/main/sem_covid/entrypoints/streamlit_visualizers/topic_modeling.py)
- sem_covid/entrypoints/streamlit_visualizers/topic_modeling.py


