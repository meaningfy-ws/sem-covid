from typing import List

import jq

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
    "social_partner_role: .fieldData.socialPartnerrole,
    "is_sector_specific": .fieldData.isSector,
    "private_or_public_sector": .fieldData.sector_privateOrPublic,
    "is_occupation_specific": .fieldData.isOccupation,
    "sectors": [.portalData.sectors[] | ."sectors::name" ],
    "occupations": [.portalData.occupations[] | .],
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

EURLEX_REFACTORING_RULES = '''.[] | {
    work: .work.value,
    title: .title.value,
    cdm_types: .cdm_types.value | split("| "),
    cdm_type_labels: .cdm_type_labels.value | split("| "),
    resource_types: .resource_types.value | split("| "),
    resource_type_labels: .resource_type_labels.value | split("| "),
    eurovoc_concepts: .eurovoc_concepts.value | split("| "),
    eurovoc_concept_labels: .eurovoc_concept_labels.value | split("| "),
    subject_matters: .subject_matters.value | split("| "),
    subject_matter_labels: .subject_matter_labels.value | split("| "),
    directory_codes: .directory_codes.value | split("| "),
    directory_codes_labels: .directory_codes_labels.value | split("| "),
    celex_numbers: .celex_numbers.value | split("| "),
    legal_elis: .legal_elis.value | split("| "),
    id_documents: .id_documents.value | split("| "),
    same_as_uris: .same_as_uris.value | split("| "),
    authors: .authors.value | split("| "),
    author_labels: .author_labels.value | split("| "),
    full_ojs: .full_ojs.value | split("| "),
    oj_sectors: .oj_sectors.value | split("| "),
    internal_comments: .internal_comments.value | split("| "),
    is_in_force: .is_in_force.value | split("| "),
    dates_document: .dates_document.value | split("| "),
    dates_created: .dates_created.value | split("| "),
    legal_dates_entry_into_force: .legal_dates_entry_into_force.value | split("| "),
    legal_dates_signature: .legal_dates_signature.value | split("| "),
    manifs_pdf: .manifs_pdf.value | split("| "),
    manifs_html: .manifs_html.value | split("| "),
    pdfs_to_download: .pdfs_to_download.value | split("| "),
    htmls_to_download: .htmls_to_download.value | split("| ")
}'''

LEGAL_INITIATIVES_REFACTORING_RULES = '''{
    work: .work.value,
    title: .title.value,
    part_of_dossiers: .part_of_dossiers.value | split("| "),
    work_sequences: .work_sequences.value | split("| "),
    related_to_works: .related_to_works.value | split("| "),
    cdm_types: .cdm_types.value | split("| "),
    cdm_type_labels: .cdm_type_labels.value | split("| "),
    resource_types: .resource_types.value | split("| "),
    resource_type_labels: .resource_type_labels.value | split("| "),
    eurovoc_concepts: .eurovoc_concepts.value | split("| "),
    eurovoc_concept_labels: .eurovoc_concept_labels.value | split("| "),
    subject_matters: .subject_matters.value | split("| "),
    subject_matter_labels: .subject_matter_labels.value | split("| "),
    directory_codes: .directory_codes.value | split("| "),
    directory_codes_labels: .directory_codes_labels.value | split("| "),
    celex_numbers: .celex_numbers.value | split("| "),
    legal_elis: .legal_elis.value | split("| "),
    id_documents: .id_documents.value | split("| "),
    same_as_uris: .same_as_uris.value | split("| "),
    authors: .authors.value | split("| "),
    author_labels: .author_labels.value | split("| "),
    full_ojs: .full_ojs.value | split("| "),
    oj_sectors: .oj_sectors.value | split("| "),
    internal_comments: .internal_comments.value | split("| "),
    is_in_force: .is_in_force.value | split("| "),
    dates_document: .dates_document.value | split("| "),
    dates_created: .dates_created.value | split("| "),
    legal_dates_entry_into_force: .legal_dates_entry_into_force.value | split("| "),
    legal_dates_signature: .legal_dates_signature.value | split("| "),
    manifs_pdf: .manifs_pdf.value | split("| "),
    manifs_html: .manifs_html.value | split("| "),
    pdfs_to_download: .pdfs_to_download.value | split("| "),
    htmls_to_download: .htmls_to_download.value | split("| ")
}'''


def transform_pwdb(pwdb_json_object: List[dict]):
    jq_programme = jq.compile(PWDB_REFACTORING_RULES.replace("\n", ""))
    transformed_pwdb = jq_programme.input(pwdb_json_object).all()
    return transformed_pwdb


def transform_eurlex(eurlex_json_object: List[dict]):
    jq_programme = jq.compile(EURLEX_REFACTORING_RULES.replace("\n", ""))
    transformed_pwdb = jq_programme.input(eurlex_json_object).all()
    return transformed_pwdb


def transform_legal_initiatives(legal_initiatives_json_object: List[dict]):
    jq_programme = jq.compile(LEGAL_INITIATIVES_REFACTORING_RULES.replace("\n", ""))
    transformed_pwdb = jq_programme.input(legal_initiatives_json_object).all()
    return transformed_pwdb
