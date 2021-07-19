from sem_covid.entrypoints import get_index_mapping


class IndicesMappingRegistry:

    @property
    def PWDB_INDEX_MAPPING(self):
        return get_index_mapping("ds_pwdb_mapping.json")

    @property
    def CELLAR_INDEX_MAPPING(self):
        return get_index_mapping("ds_legal_initiatives_mapping.json")

    @property
    def EU_TIMELINE_MAPPING(self):
        return get_index_mapping("ds_eu_timeline_mapping.json")

    @property
    def IRELAND_TIMELINE_MAPPING(self):
        return get_index_mapping("ds_ireland_timeline_mapping.json")
