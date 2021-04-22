Feature: Test ElasticSearch indexes

  Scenario Outline: PWDB Index Search
    Given I have the query <query_file>
    When I run the query against the index
    Then the result count is <result_count>

    Examples:
      | query_file                                                                                      | result_count |
      | query_background_description_full_text_match_covid.json                                         | 693          |
      | query_background_description_full_text_match_employment.json                                    | 297          |
      | query_title_full_text_match_covid.json                                                          | 160          |
      | query_title_full_text_match_employment.json                                                     | 71           |
      | query_content_of_measure_description_full_text_match_covid.json                                 | 452          |
      | query_content_of_measure_description_full_text_match_employment.json                            | 420          |
      | query_background_description_fuzzy_work_and_travel.json                                         | 367          |
      | query_background_description_fuzzy_stay_at_home.json                                            | 113          |
      | query_title_fuzzy_work_and_travel.json                                                          | 117          |
      | query_title_fuzzy_stay_at_home.json                                                             | 16           |
      | query_content_of_measure_description_fuzzy_stay_at_home.json                                    | 151          |
      | query_content_of_measure_description_fuzzy_work_and_travel.json                                 | 487          |
      | query_background_description_match_phrase_European_Commission.json                              | 21           |
      | query_background_description_match_phrase_European_Union.json                                   | 7            |
      | query_title_match_phrase_European_Commission.json                                               | 1            |
      | query_title_match_phrase_European_Union.json                                                    | 0            |
      | query_content_of_measure_description_match_phrase_European_Commission.json                      | 7            |
      | query_content_of_measure_description_match_phrase_European_Union.json                           | 8            |
      | query_background_description_common_terms_search_the_national_unemployment_level.json           | 3            |
      | query_background_description_common_terms_search_benefits_for_vulnerable_families.json          | 1            |
      | query_title_common_phrase_search_the_national_unemployment_level.json                           | 0            |
      | query_title_common_phrase_search_benefits_for_vulnerable_families.json                          | 0            |
      | query_content_of_measure_description_common_phrase_search_the_national_unemployment_level.json  | 3            |
      | query_content_of_measure_description_common_phrase_search_benefits_for_vulnerable_families.json | 3            |
      | category_filtering_Employment_protection_and_retention.json                                     | 103          |
      | target_group_filtering_disabled_workers.json                                                    | 28           |
      | target_group_filtering_unemployed_and_SMEs.json                                                 | 2            |
      | country_filtering_Austria.json                                                                  | 53           |
      | country_filtering_Austria_or_Ireland.json                                                       | 86           |
      | documents_filtering_start_date_end_date_range.json                                              | 408          |