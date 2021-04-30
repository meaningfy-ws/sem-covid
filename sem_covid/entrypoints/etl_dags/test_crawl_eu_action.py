from sem_covid import config
import pandas as pd
print(config.CRAWLER_EU_TIMELINE_SPOKEPERSONS)


df = pd.read_json(config.CRAWLER_EU_TIMELINE_SPOKEPERSONS)
author = 'Johannes Bahrke'
print(df[df['Name'] == author ]['Topics'][0])
