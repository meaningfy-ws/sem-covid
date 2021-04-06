"""
    Fixtures and Fake adapters necessary for unit testing
"""
import json

import pytest
import pandas as pd

from ml_experiments.services.pwdb_base_experiment import PWDBBaseExperiment
from ml_experiments.services.sc_wrangling.pwdb_transformer import transform_pwdb


@pytest.fixture(scope="session")
def raw_pwdb_data():
    raw_sample = [{
        "fieldData": {
            "title": "Hardship case fund: Safety net for self-employed",
            "title_nationalLanguage": "H\u00e4rtefall-Fonds: Sicherheitnetz f\u00fcr Selbstst\u00e4ndige",
            "d_startDate": "03/27/2020",
            "d_endDate": "04/30/2021",
            "calc_country": "Austria",
            "calc_minorCategory": "Income protection beyond short-time work",
            "calc_subMinorCategory": "Extensions of  income support to workers not covered by any kind of protection scheme",
            "calc_identifier": "AT-2020-13/212",
            "dateType": "Temporary",
            "calc_creationDay": "03/31/2020",
            "calc_lastUpdate": "01/04/2021",
            "descriptionBackgroundInfo": "As part of the \u20ac4 billion fund to mitigate the effects of the Corona crisis, which the Austrian national government and the social partners presented on 14 March 2020, they also presented two hardship funds: one for self-employed in one person companies; and the other for family-run businesses. This was complementary to other measures (see case AT-2020-12-/229), as those two target groups would not be able to profit from the short-time working schemes.\r\r",
            "descriptionContentOfMeasure": "The support is a one-off payment and does not have to be paid back. In addition, affected owners of one person companies may also obtain funds from the 'emergency fund' (Notfallfonds). The payments cannot be accumulated though. The hardship fund for self-employed is divided in two phases:\r\r* **Phase 1**: Applications are possible until 17 April 2020. Eligible are those who can prove that they are no longer able to cover the running costs or are affected by an officially ordered ban on entry due to COVID-19 or have a drop in sales of at least 50% compared to the same month of the previous year. The amount of the funding is \u20ac500 if the net income p.a. was below \u20ac6,000 and \u20ac1,000 if it was above \u20ac6,000. The upper income threshold (above which no grant is paid) is \u20ac33,812 net in the last year for which a tax assessment is available. It essentially applies to one person enterprises (including agricultural and forestry and private accommodation rents) and freelance workers.\r* **Phase 2**: Applications start on 20 April 2020. The grant depends on the income loss and lies at maximum at \u20ac2,000 per month for up to three months. No upper income threshold applies, and small companies with less than ten employees and liberal professions are eligible in addition to the group eligible in phase 1. Negotiations with NGOs are currently ongoing.\rAll applicants (regardless of whether an application has already been submitted in phase 1) will have the same maximum total amount of funding of up to \u20ac6,000. \r\rIn general, applications for the Hardship Fund can be submitted until 31 January 2021. ",
            "descriptionUseOfMeasure": "Information from 1 April: Around 100,000 applications for phase 1 were counted so far. The total funds for the hardship fund were increased from \u20ac1 to 2 billion.\r\rInformation from 20 April: The first phase has been completed with 144,000 applications made. A total of \u20ac121 million. was paid out in the first phase. \r\rAs of mid-September, a total of almost 195,000 people have been supported in phases one and two and around \u20ac528.7 million have been paid out. In the most recent period under review (mid-July to mid-August), an average of around \u20ac1,200 was paid out in each case.\r\rAs of mid-October 2020, around 203,000 people have applied for assistance from the Corona hardship fund since the beginning and \u20ac700 million have been spent. On average, \u20ac1,200 euros were paid per individual in the period between 16 September and 15 October 2020. \rAccording to a survey conducted in July and August 2020 by KMU Research Austria, 57 percent of one-person enterprises have taken advantage of government support measures in connection with the COVID-19 crisis. Of these, almost all entrepreneurs have applied for the hardship fund. Significantly fewer have also applied for tax and duty deferrals (36%), installment payments or deferrals of social security contributions (35%) and fixed cost subsidies (29%). ",
            "descriptionInvolvementOfSocialPartners": "The Federal Economic Chamber was involved.",
            "socialPartner_form": "Direct consultation",
            "socialPartner_role": "Agreed (outcome)",
            "calc_githubURL": "https://static.eurofound.europa.eu/covid19db/cases/AT-2020-13_212.html",
            "isOccupation": "No",
            "isSector": "No",
            "sector_privateOrPublic": "Not specified",
            "calc_type": "Legislations or other statutory regulations",
            "statusOfRegulation": "Entirely new measure "
        },
        "portalData": {
            "sources": [
                {
                    "recordId": "74",
                    "sources::title": "Hardship fund: safety net for the self-employed (H\u00e4rtefall-Fonds: Sicherheitsnetz f\u00fcr Selbst\u00e4ndige)",
                    "sources::url": "https://www.wko.at/service/haertefall-fonds-epu-kleinunternehmen.html",
                    "sources::d_date": "03/31/2020",
                    "modId": "7"
                },
                {
                    "recordId": "76",
                    "sources::title": "Haertefallfonds - Regulation",
                    "sources::url": "https://www.wko.at/service/haertefall-fonds-phase-2.html",
                    "sources::d_date": "03/31/2020",
                    "modId": "7"
                },
                {
                    "recordId": "77",
                    "sources::title": "H\u00e4rtefallfonds soll bis zu 6.000 Euro auszahlen",
                    "sources::url": "https://orf.at/stories/3159474/",
                    "sources::d_date": "03/26/2020",
                    "modId": "6"
                },
                {
                    "recordId": "665",
                    "sources::title": "Uptake of hardship fund - first phase",
                    "sources::url": "https://www.ots.at/presseaussendung/OTS_20200419_OTS0021/haertefall-fonds-geht-in-zweite-phase-informationen-und-services",
                    "sources::d_date": "04/20/2020",
                    "modId": "1"
                },
                {
                    "recordId": "890",
                    "sources::title": "Improvements in the hardship fund: comeback bonus and higher minimum support for the self-employed",
                    "sources::url": "https://news.wko.at/news/oesterreich/Nachbesserungen-im-Haertefall-Fonds:-Comeback-Bonus-und-h.html",
                    "sources::d_date": "05/27/2020",
                    "modId": "0"
                },
                {
                    "recordId": "1557",
                    "sources::title": "WKO calls for extension of hardship case fund",
                    "sources::url": "https://kurier.at/wirtschaft/haertefallfonds-wirtschaftskammer-will-laengeren-foerderzeitraum/401033111",
                    "sources::d_date": "09/16/2020",
                    "modId": "0"
                },
                {
                    "recordId": "1751",
                    "sources::title": "NPO and hoardship fund are extended",
                    "sources::url": "https://www.ots.at/presseaussendung/OTS_20201007_OTS0113/koestinger-npo-und-haertefall-fonds-werden-verlaengert",
                    "sources::d_date": "10/07/2020",
                    "modId": "0"
                },
                {
                    "recordId": "1808",
                    "sources::title": "Bundesministerium f\u00fcr Finanzen - Information",
                    "sources::url": "https://www.bmf.gv.at/public/top-themen/corona-hilfspaket-faq.html",
                    "sources::d_date": "10/13/2020",
                    "modId": "0"
                },
                {
                    "recordId": "2370",
                    "sources::title": "On average \u20ac1,200 paid",
                    "sources::url": "https://orf.at/stories/3189639/",
                    "sources::d_date": "11/13/2020",
                    "modId": "0"
                }
            ],
            "actors": [
                {
                    "recordId": "1",
                    "actors::name": "National government",
                    "modId": "3"
                },
                {
                    "recordId": "4",
                    "actors::name": "Employers' organisations",
                    "modId": "3"
                }
            ],
            "targetGroups": [
                {
                    "recordId": "31",
                    "targetGroups::name": "Self-employed",
                    "modId": "15"
                },
                {
                    "recordId": "55",
                    "targetGroups::name": "Solo-self-employed",
                    "modId": "16"
                },
                {
                    "recordId": "63",
                    "targetGroups::name": "One person or microenterprises",
                    "modId": "12"
                }
            ],
            "funding": [
                {
                    "recordId": "7",
                    "funding::name": "National funds",
                    "modId": "0"
                }
            ],
            "occupations": [],
            "sectors": [],
            "updates": [
                {
                    "recordId": "42",
                    "updates::d_date": "05/27/2020",
                    "updates::description": "An expansion of the safety net self-employed was announced on 27 May. Next to the prolongation of the period over which grants can be obtained from three to six months, a so called 'come back bonus' of \u20ac500 was introduced. This will be added automatically to already existing grants. Including this bonus the minimum amount of the grant will be raised to \u20ac1,000. Another novelty is that also pensioners in marginal employment are going to be eligible for the grant. ",
                    "modId": "2"
                },
                {
                    "recordId": "284",
                    "updates::d_date": "09/16/2020",
                    "updates::description": "The Federal Economic Chamber (WKO) has called for an extension of the measure - an application should be possible for twelve instead of six months. ",
                    "modId": "1"
                },
                {
                    "recordId": "349",
                    "updates::d_date": "10/07/2020",
                    "updates::description": "The Council of Ministers agreed on the extension of the measure as requested by the WKO on 7 October 2020. The duration is extended to twelve months, i.e. from 16 March 2020 to 15 March 2021. The maximum amount received is \u20ac2,500 per month, i.e. \u20ac30,000 in total. The hardship fund is intended to help micro-enterprises, freelancers and farmers who have financial difficulties due to the corona crisis.",
                    "modId": "3"
                }
            ],
            "regions": []
        },
        "recordId": "95",
        "modId": "137"
    }]

    return raw_sample


class FakeRequest(object):

    def get(self, *args, **kwargs):
        pass

    def raise_for_status(self, *args, **kwargs):
        pass

    @property
    def content(self):
        return raw_pwdb_data()


class FakeMinioAdapter(object):
    def get_object(self, object_name: str = None) -> bytes:
        """
            The important step is to create testing dataframe and most important
            is to create the same column names and values types
            :return: dict object
        """

        # data_object = {'Title': ['title_one', 'title_two'], 'Background information': ['bi_one', 'bi_two'],
        #                'Content of measure': ['cm_one', 'cm_two'], 'Category': ['cm_one', 'cm_two'],
        #                'Subcategory': ['sub_one', 'sub_two'], 'Type of measure': ['tom_one', 'tom_two'],
        #                'Target groups': [['tg_one', 'tg_two'], ['tg_one_first', 'tg_two_second']]}
        return bytes(json.dumps(raw_pwdb_data()), encoding="utf8")

    def empty_bucket(self):
        pass

    def put_object(self, object_name: str, content):
        return len(str(content))


class ForTestingBasePWDBExperiment(PWDBBaseExperiment):
    def model_training(self, *args, **kwargs):
        pass

    def model_evaluation(self, *args, **kwargs):
        pass

    def model_validation(self, *args, **kwargs):
        pass


@pytest.fixture(scope="session")
def base_experiment():
    return ForTestingBasePWDBExperiment(FakeMinioAdapter(), FakeRequest())


@pytest.fixture(scope="session")
def transformed_pwdb_json():
    return transform_pwdb(raw_pwdb_data())


@pytest.fixture(scope="session")
def transformed_pwdb_dataframe():
    return pd.DataFrame.from_records(transformed_pwdb_json())
