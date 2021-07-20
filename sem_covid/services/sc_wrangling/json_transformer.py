import logging
from typing import List

import jq

logger = logging.getLogger(__name__)

PWDB_REFACTORING_RULES = '''.[] | {
    "identifier": .recordId,
    "title": .fieldData.title,
    "title_national_language": .fieldData.title_nationalLanguage,
    "country": .fieldData.calc_country,
    "start_date": .fieldData.d_startDate,
    "end_date": .fieldData.d_endDate,
    "date_type": .fieldData.dateType,
    "type_of_measure": .fieldData.calc_type,
    "status_of_regulation": .fieldData.statusOfRegulation,
    "category": .fieldData.calc_minorCategory,
    "subcategory": .fieldData.calc_subMinorCategory,
    "creation_date": .fieldData.calc_creationDay,
    "background_info_description": .fieldData.descriptionBackgroundInfo,
    "content_of_measure_description": .fieldData.descriptionContentOfMeasure,
    "use_of_measure_description": .fieldData.descriptionUseOfMeasure,
    "actors": [.portalData.actors[] |  ."actors::name" ],
    "target_groups": [.portalData.targetGroups[] | ."targetGroups::name"],
    "funding": [.portalData.funding[] | ."funding::name" ],
    "involvement_of_social_partners_description": .fieldData.descriptionInvolvementOfSocialPartners,
    "social_partner_involvement_form": .fieldData.socialPartnerform,
    "social_partner_role": .fieldData.socialPartnerrole,
    "is_sector_specific": .fieldData.isSector,
    "private_or_public_sector": .fieldData.sector_privateOrPublic,
    "is_occupation_specific": .fieldData.isOccupation,
    "sectors": [.portalData.sectors[] | ."sectors::name" ],
    "occupations": [.portalData.occupations[] | ."occupations::name" ],
    "sources": .portalData | [ .sources[] | {"title" : ."sources::title", "url": ."sources::url" } ],
}'''

# This PWDB_REFACTORING_RULES is deprecated,
# because they do not conform to the index in ElasticSearch and are not in the index field name standard.

PWDB_REFACTORING_RULES_DEPRECATED = '''.[] | {
    "Identifier": .recordId,
    "Title": .fieldData.title,
    "Title (national language)": .fieldData.title_nationalLanguage,
    "Country": .fieldData.calc_country,
    "Start date": .fieldData.d_startDate,
    "End date": .fieldData.d_endDate,
    "Date type": .fieldData.dateType,
    "Type of measure": .fieldData.calc_type,
    "Status of regulation": .fieldData.statusOfRegulation,
    "Category": .fieldData.calc_minorCategory,
    "Subcategory": .fieldData.calc_subMinorCategory,
    "Case added": .fieldData.calc_creationDay,
    "Background information": .fieldData.descriptionBackgroundInfo,
    "Content of measure": .fieldData.descriptionContentOfMeasure,
    "Use of measure": .fieldData.descriptionUseOfMeasure,
    "Actors": [.portalData.actors[] |  ."actors::name" ],
    "Target groups": [.portalData.targetGroups[] | ."targetGroups::name"],
    "Funding": [.portalData.funding[] | ."funding::name" ],
    "Views of social partners": .fieldData.descriptionInvolvementOfSocialPartners,
    "Form of social partner involvement": .fieldData.socialPartnerform,
    "Role of social partners": .fieldData.socialPartnerrole,
    "Is sector specific": .fieldData.isSector,
    "Private or public sector": .fieldData.sector_privateOrPublic,
    "Is occupation specific": .fieldData.isOccupation,
    "Sectors": [.portalData.sectors[] | ."sectors::name" ],
    "Occupations": [.portalData.occupations[] | .],
    "Sources": .portalData | [ .sources[] | {"Title" : ."sources::title", "URL": ."sources::url" } ],
}'''

EU_CELLAR_REFACTORING_RULES = '''.| {
    work: (.work // "") | tostring ,
    title: (.title // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
cdm_types: (.cdm_types // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
cdm_type_labels: (.cdm_type_labels // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
resource_types: (.resource_types // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
resource_type_labels: (.resource_type_labels // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
eurovoc_concepts: (.eurovoc_concepts // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
eurovoc_concept_labels: (.eurovoc_concept_labels // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
subject_matters: (.subject_matters // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
subject_matter_labels: (.subject_matter_labels // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
directory_codes: (.directory_codes // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
directory_codes_labels: (.directory_codes_labels // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
celex_numbers: (.celex_numbers // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
legal_elis: (.legal_elis // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
id_documents: (.id_documents // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
same_as_uris: (.same_as_uris // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
authors: (.authors // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
author_labels: (.author_labels // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
full_ojs: (.full_ojs // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
oj_sectors: (.oj_sectors // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
internal_comments: (.internal_comments // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
is_in_force: (.is_in_force // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
dates_document: (.dates_document // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
dates_created: (.dates_created // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
legal_dates_entry_into_force: (.legal_dates_entry_into_force // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
legal_dates_signature: (.legal_dates_signature // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
manifs_pdf: (.manifs_pdf // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
manifs_html: (.manifs_html // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
pdfs_to_download: (.pdfs_to_download // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
htmls_to_download: (.htmls_to_download // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
dossiers: (.dossiers // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
related_works: (.related_works // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end),
work_sequences: (.work_sequences // null) | (if . == "" or . == [] or .== null then null else ( . | tostring | split("| ") ) end)  
}'''


def transform_pwdb(pwdb_json_object: List[dict]):
    jq_programme = jq.compile(PWDB_REFACTORING_RULES.replace("\n", ""))
    transformed_pwdb = jq_programme.input(pwdb_json_object).all()
    return transformed_pwdb


def transform_eu_cellar_item(item_json_text: dict) -> dict:
    jq_programme = jq.compile(EU_CELLAR_REFACTORING_RULES.replace("\n", ""))
    return jq_programme.input(item_json_text).first()
