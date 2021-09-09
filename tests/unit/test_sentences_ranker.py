#!/usr/bin/python3

# test_sentences_ranker.py
# Date:  07.09.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com


from sem_covid.services.sc_wrangling.sentences_ranker import *


def test_top_k_mean():
    data = [1, 2, 3, 4]
    k = 10
    result = top_k_mean(data=data, top_k=k)
    assert result == 1


def test_textual_tfidf_ranker():
    textual_chunks = ['According to the Employment Relationship Act, when a company temporarily fails to provide',
                      ' The wage basis is determined at the worker’s average monthly wage for full-time work',
                      ' On the other hand, if a worker cannot carry out his work due to force majeure',
                      ' The temporary laid-off worker is obliged to respond to the employer’s invitation',
                      'The measure being examined, attempting to cushion the economic effects of the COVID-19 epidemic',
                      ' This reimbursement is funded with the state budget',
                      ' Reimbursement is limited to the average monthly salary in 2019',
                      'The maximum length of receiving compensation is from 13 March to 31 May',
                      ' To be eligible for the reimbursements, a company had to demonstrate a 20%',
                      '']
    k = 10
    result = textual_tfidf_ranker(textual_chunks=textual_chunks, top_k=k)
    assert type(result) == list
    assert len(result) == len(textual_chunks)

