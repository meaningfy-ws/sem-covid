import pandas as pd

from sem_covid.services.store_registry import StoreRegistry


def test_feature_store():
    """
     Mystery fail in our code [Dataframe from ES is not same as original Dataframe]
    """
    feature_store = StoreRegistry.es_feature_store()
    df = pd.DataFrame([{"A": "a", "B": "b"}])
    print(df)
    feature_name = 'tmp_test_feature_store'
    feature_store.put_features(feature_name, df)
    remote_df = feature_store.get_features(features_name=feature_name)
    print(remote_df)
    #remote_df.index.name = None
    #df.index.name = None
    print(pd.concat([df, remote_df]))
    assert df.equals(remote_df)
