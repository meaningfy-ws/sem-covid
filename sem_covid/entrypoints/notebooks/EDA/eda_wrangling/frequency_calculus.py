from collections import Counter

import pandas as pd


def calculate_frequency(data: pd.Series, title: str, relative: bool = False) -> pd.DataFrame:
    """
    Functions to calculate frequency for textual data
    """
    observation_type_name = 'Absolute freq' if not relative else 'Relative freq'
    data.dropna(inplace=True)
    observation = pd.DataFrame(Counter(data).most_common(10), columns=[title, observation_type_name])
    if relative:
        observation[observation_type_name] /= observation[observation_type_name].sum() / 100
        observation[observation_type_name] = round(observation[observation_type_name], 2)

    return observation
