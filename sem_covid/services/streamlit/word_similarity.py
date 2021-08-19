
import streamlit as st
import pandas as pd
import networkx as nx
from d3graph import d3graph

from sem_covid.services.store_registry import store_registry

st.title('Semantic similarity graph')

st.text_input("Introduce word")

threshold_slider = st.slider('Threshold', min_value=0.0, max_value=1.0, step=0.1, value=0.4)
number_of_neighbours_slider = st.slider('Number of Neighbours', min_value=1, max_value=5, step=1, value=2)
graph_depth_slider = st.slider('Graph Depth', min_value=2, max_value=5, step=1, value=2)

sliders = [threshold_slider, number_of_neighbours_slider, graph_depth_slider]

for slider in sliders:
    st.write(slider)

