import mlflow
from gensim.models import KeyedVectors
from sklearn import preprocessing
from sem_covid import config
from pycaret.classification import *
from sem_covid.services.data_registry import Dataset, LanguageModel
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

SIMPLE_CLASS_COLUMNS = ['category', 'subcategory', 'type_of_measure', 'target_groups',
                        'actors']

CLASS_TEXTUAL_LABELS = ['category_label', 'subcategory_label', 'type_of_measure_label', 'target_groups_label',
                        'actors_label']

CLASS_COLUMNS = ['businesses', 'citizens', 'workers', 'category', 'subcategory', 'type_of_measure', 'target_groups',
                 'actors', 'category_label', 'subcategory_label', 'type_of_measure_label', 'target_groups_label',
                 'actors_label']

TRAIN_CLASSES = ['businesses', 'citizens', 'workers', 'category', 'subcategory', 'type_of_measure', 'target_groups',
                 'actors']

EMBEDDING_COLUMN = "embeddings"


class FeatureEngineering:
    """
    this class performs

    - the document embedding
    - class re-organisation
    """

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
        self.l2v_dict = KeyedVectors.load_word2vec_format(law2vec_path, encoding="utf-8")

    def transform_data(self):
        pwdb_dataframe = self.df
        new_columns = {'businesses': BUSINESSES, 'citizens': CITIZENS, 'workers': WORKERS}
        refactored_pwdb_df = pwdb_dataframe['target_groups']
        for column, class_set in new_columns.items():
            pwdb_dataframe[column] = refactored_pwdb_df.apply(lambda x: any(item in class_set for item in x))
            pwdb_dataframe[column].replace({True: 1, False: 0}, inplace=True)
        pwdb_dataframe['target_groups'] = pwdb_dataframe['target_groups'].apply(lambda x: "|".join(x))
        pwdb_dataframe['actors'] = pwdb_dataframe['actors'].apply(lambda x: "|".join(x))
        for column in SIMPLE_CLASS_COLUMNS:
            le = preprocessing.LabelEncoder()
            le.fit(pwdb_dataframe[column])
            pwdb_dataframe[column + '_label'] = pwdb_dataframe[column]
            pwdb_dataframe[column] = le.transform(pwdb_dataframe[column])

        self.df = pwdb_dataframe
        self.df = self.df.set_index(self.df.columns[0])
        self.df[EMBEDDING_COLUMN] = self.df[TEXTUAL_COLUMNS].agg(" ".join, axis=1)
        self.df[EMBEDDING_COLUMN] = self.df[EMBEDDING_COLUMN].apply(lambda x: text_to_vector(x, self.l2v_dict))

    def store_feature_set(self):

        input_features_name = self.feature_store_name + "_x"
        output_features_name = self.feature_store_name + "_y"
        feature_store = StoreRegistry.es_feature_store()
        matrix_df = pd.DataFrame(list(self.df[EMBEDDING_COLUMN].values))
        feature_store.put_features(features_name=input_features_name, content=matrix_df)
        feature_store.put_features(features_name=output_features_name, content=pd.DataFrame(self.df[CLASS_COLUMNS]))

    def execute(self):
        self.load_data()
        self.validate_data()
        self.load_language_model()
        self.transform_data()
        self.store_feature_set()


class ModelTraining:

    def __init__(self, feature_store_name: str, experiment_name: str, train_classes: list = None):
        self.feature_store_name = feature_store_name
        self.experiment_name = experiment_name
        self.dataset_x = pd.DataFrame()
        self.dataset_y = pd.DataFrame()
        self.train_classes = train_classes if train_classes else TRAIN_CLASSES

    def load_feature_set(self):
        feature_store = StoreRegistry.es_feature_store()
        input_features_name = self.feature_store_name + "_x"
        output_features_name = self.feature_store_name + "_y"
        self.dataset_x = feature_store.get_features(input_features_name)
        self.dataset_y = feature_store.get_features(output_features_name)

    def validate_feature_set(self):
        assert self.dataset_x is not None
        assert self.dataset_y is not None
        for column in self.train_classes:
            assert column in self.dataset_y.columns

    def train_model(self):
        for class_name in self.train_classes:
            dataset = self.dataset_x
            dataset[class_name] = self.dataset_y[class_name].values
            train_data = dataset
            train_data.reset_index(inplace=True, drop=True)
            experiment = setup(data=train_data,
                               target=class_name,
                               log_experiment=True,
                               experiment_name=f"{self.experiment_name}_{class_name}",
                               silent=True)
            best_model = compare_models()
            tuned_model = tune_model(best_model, n_iter=200, choose_better=True, optimize='F1')
            final_model = finalize_model(tuned_model)
            del dataset
            del train_data

    def execute(self):
        self.load_feature_set()
        self.validate_feature_set()
        mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
        self.train_model()


PWDB_FEATURE_STORE_NAME = 'fs_pwdb'


class PWDBClassifiers:

    @classmethod
    def feature_engineering(cls):
        worker = FeatureEngineering(feature_store_name=PWDB_FEATURE_STORE_NAME)
        worker.execute()

    @classmethod
    def model_training(cls):
        worker = ModelTraining(feature_store_name=PWDB_FEATURE_STORE_NAME,
                               experiment_name="PyCaret_pwdb")
        worker.execute()
