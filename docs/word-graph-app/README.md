# *WP3.4[BONUS] - Discovery WordGraph application*

## **Discovery WordGraph application**

It is an application to visualize the semantic relations in a graph form, between different words based on the trained language model named **M3**.

## **How to use**
The application provides a set of parameters that can be configured before starting the graph generation (action that is done by pressing the "Generate graph" button). 

The set of parameters that can be configured: 
- Introduce word -  in this field you can enter the word from which you want the graph to be generated, this word will be the root for WordGraph (for example “covid19”). 
- Select similarity - in this field you can choose which type of similarity metric to use, as the following similarity metrics are available: 
    - cosine
    - euclidean
    - hamming 
- Threshold - this option allows you to select a threshold for word links. If the similarity between words is less than the threshold value then the link will not be placed in WordGraph. This option allows you to filter links by similarity value.
- Number of neighbours - this option allows you to select the maximum number of neighbors that a node can have in the graph.

## **How access the application?**
This web application can be accessed [here](http://srv.meaningfy.ws:8501/).

[**Source code**](
sem_covid/entrypoints/streamlit_visualizers/word_similarity.py)
- sem_covid/entrypoints/streamlit_visualizers/word_similarity.py


