import mlflow
import pandas as pd
from gensim.models import KeyedVectors
from sklearn import model_selection
from sklearn.base import ClassifierMixin
from sklearn.ensemble import RandomForestClassifier

from sem_covid import config
from sem_covid.services.base_pipeline import BaseExperiment
from sem_covid.services.data_registry import Dataset, LanguageModel
from sem_covid.services.sc_wrangling.evaluation_metrics import model_evaluation_metrics
from sem_covid.services.sc_wrangling.mean_vectorizer import text_to_vector
from sem_covid.services.store_registry import StoreRegistry

BUSINESSES = {'Companies providing essential services', 'Contractors of a company', 'Larger corporations',
              'One person or microenterprises', 'Other businesses', 'SMEs', 'Sector specific set of companies',
              'Solo-self-employed', 'Start-ups'}

CITIZENS = {'Children (minors)', 'Disabled', 'Migrants', 'Older citizens', 'Other groups of citizens', 'Parents',
            'People in care facilities', 'Refugees', 'Single parents', 'The COVID-19 risk group', 'Women',
            'Youth (18-25)'}

WORKERS = {'Cross-border commuters', 'Disabled workers', 'Employees in standard employment', 'Female workers',
           'Migrants in employment', 'Older people in employment (aged 55+)', 'Other groups of workers',
           'Parents in employment', 'Particular professions', 'Platform workers', 'Posted workers',
           'Refugees in employment', 'Seasonal workers', 'Self-employed', 'Single parents in employment',
           'The COVID-19 risk group at the workplace', 'Undeclared workers', 'Unemployed', 'Workers in care facilities',
           'Workers in essential services', 'Workers in non-standard forms of employment',
           'Youth (18-25) in employment'}

TEXTUAL_COLUMNS = ['title', 'background_info_description', 'content_of_measure_description',
                   'use_of_measure_description', 'involvement_of_social_partners_description']

CLASS_COLUMNS = ['businesses', 'citizens', 'workers']

TRAIN_COLUMNS = ['x_train', 'x_test', 'y_train', 'y_test', 'class_name']


class FeatureEngineering:

    def __init__(self, feature_store_name: str):
        self.df = pd.DataFrame()
        self.l2v_dict = {}
        self.feature_store_name = feature_store_name

    def load_data(self):
        self.df = Dataset.PWDB.fetch()

    def validate_data(self):
        for column in TEXTUAL_COLUMNS:
            assert column in self.df.columns

    def load_language_model(self):
        law2vec = LanguageModel.LAW2VEC.fetch()
        law2vec_path = LanguageModel.LAW2VEC.path_to_local_cache()
        law2vec_format = KeyedVectors.load_word2vec_format(law2vec_path, encoding="utf-8")
        self.l2v_dict = {w: vec for w, vec in zip(law2vec_format.index_to_key, law2vec_format.vectors)}

    def transform_data(self):
        pwdb_dataframe = self.df
        new_columns = {'businesses': BUSINESSES, 'citizens': CITIZENS, 'workers': WORKERS}
        refactored_pwdb_df = pwdb_dataframe['target_groups']
        for column, class_set in new_columns.items():
            pwdb_dataframe[column] = refactored_pwdb_df.apply(lambda x: any(item in class_set for item in x))
            pwdb_dataframe[column].replace({True: 1, False: 0}, inplace=True)
        self.df = pwdb_dataframe
        self.df = self.df.set_index(self.df.columns[0])
        self.df["text_data"] = self.df[TEXTUAL_COLUMNS].agg(" ".join, axis=1)
        self.df["text_data"] = self.df["text_data"].apply(lambda x: text_to_vector(x, self.l2v_dict))

    def store_feature_set(self):

        input_features_name = self.feature_store_name + "_x"
        output_features_name = self.feature_store_name + "_y"
        feature_store = StoreRegistry.es_feature_store()
        matrix_df = pd.DataFrame(list(self.df["text_data"].values))
        feature_store.put_features(features_name=input_features_name, content=matrix_df)
        feature_store.put_features(features_name=output_features_name, content=pd.DataFrame(self.df[CLASS_COLUMNS]))

    def execute(self):
        self.load_data()
        self.validate_data()
        self.load_language_model()
        self.transform_data()
        self.store_feature_set()


class ModelTraining:

    def __init__(self, model: ClassifierMixin, feature_store_name: str):
        self.trained_models = []
        self.model = model
        self.feature_store_name = feature_store_name
        self.train_features = pd.DataFrame()
        self.evaluation_models = []

    def load_feature_set(self):
        feature_store = StoreRegistry.es_feature_store()
        input_features_name = self.feature_store_name + "_x"
        output_features_name = self.feature_store_name + "_y"
        input_features = feature_store.get_features(input_features_name)
        input_features = input_features.values.tolist()
        output_features = feature_store.get_features(output_features_name)
        x_train_list = list()
        x_test_list = list()
        y_train_list = list()
        y_test_list = list()
        for column in output_features.columns:
            x_train, x_test, y_train, y_test = model_selection.train_test_split(input_features,
                                                                                output_features[column].values,
                                                                                random_state=42, test_size=0.3,
                                                                                shuffle=True)
            x_train_list.append(list(x_train))
            x_test_list.append(list(x_test))
            y_train_list.append(list(y_train))
            y_test_list.append(list(y_test))
        train_test_dataset = {"x_train": x_train_list, "x_test": x_test_list,
                              "y_train": y_train_list, "y_test": y_test_list,
                              "class_name": output_features.columns}
        self.train_features = pd.DataFrame.from_dict(train_test_dataset)

    def validate_feature_set(self):
        for column in TRAIN_COLUMNS:
            assert column in self.train_features.columns

    def train_model(self):
        for it, row in self.train_features.iterrows():
            model = self.model
            model = model.fit(row['x_train'],
                              row['y_train'])
            self.trained_models.append((model, row))

    def evaluate_model(self):
        for trained_model, row in self.trained_models:
            prediction = trained_model.predict(row['x_test'])
            evaluation = model_evaluation_metrics(
                row['y_test'], prediction)
            self.evaluation_models.append((evaluation, row['class_name']))

    def track_ml_run(self):
        mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(experiment_name="PWDB_target_group_l1(RandomForest, law2vec200d)")
        for evaluation, class_name in self.evaluation_models:
            with mlflow.start_run():
                mlflow.log_param("class_name", class_name)
                mlflow.log_metrics(evaluation)

    def execute(self):
        self.load_feature_set()
        self.validate_feature_set()
        self.train_model()
        self.evaluate_model()
        self.track_ml_run()


PWDB_FEATURE_STORE_NAME = 'fs_pwdb_tg1'


class RandomForestPWDBExperiment:

    @classmethod
    def feature_engineering(cls):
        worker = FeatureEngineering(feature_store_name=PWDB_FEATURE_STORE_NAME)
        worker.execute()

    @classmethod
    def model_training(cls):
        classifier = RandomForestClassifier()
        worker = ModelTraining(model=classifier, feature_store_name=PWDB_FEATURE_STORE_NAME)
        worker.execute()
