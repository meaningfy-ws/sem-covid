FROM apache/airflow:2.2.2-python3.8

# quick sudo
USER root
RUN apt-get update && apt-get install make && apt-get install build-essential -y

# back to normal user
USER airflow

# requirements-airflow.txt shall be made availble from teh **sem-covid** GitHub repository
COPY requirements-airflow.txt /opt/airflow

# working in the /opt/airflow
WORKDIR /opt/airflow

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements-airflow.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.2/constraints-no-providers-3.8.txt"
#RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements-dev.txt
RUN python -m spacy download en_core_web_sm