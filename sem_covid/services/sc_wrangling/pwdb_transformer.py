
from typing import List

import jq

PWDB_REFACTORING_RULES = '''.[] | {
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
    "Sectors": [.portalData.sectors[] | ."sectors::name" ], 
    "Occupations": [.portalData.occupations[] | ."occupations::name"], 
    "Funding": [.portalData.funding[] | ."funding::name" ],
    "Views of social partners": .fieldData.descriptionInvolvementOfSocialPartners,
    "Form of social partner involvement": .fieldData.socialPartnerform,
    "Role of social partners": .fieldData.socialPartnerrole,
    "Is sector specific": .fieldData.isSector,
    "Private or public sector": .fieldData.sector_privateOrPublic,
    "Is occupation specific": .fieldData.isOccupation,
    "Sectors": [.portalData.sectors[] | ."sectors::name" ],
    "Occupations": [.portalData.occupations[] | .],
    "Sources": [.portalData.sources[] | ."sources::url" ],
}'''


def transform_pwdb(pwdb_json_object: List[dict]):
    jq_programme = jq.compile(PWDB_REFACTORING_RULES.replace("\n", ""))
    transformed_pwdb = jq_programme.input(pwdb_json_object).all()
    return transformed_pwdb
