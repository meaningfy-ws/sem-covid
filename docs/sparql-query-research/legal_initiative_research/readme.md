# Cellar investigation into Legal Initiative works   

Xavier provided the hint: 
From the first link you provided, I see the documents have Ares reference.
It can be identified as `immc:Ares(2020)6555120`.
FYI, any work having a `pi_com` psi is considered from the public access and is probably on the BRP (EC better regulation proposals) as well.

# Legal Initiatives have a document_id PREFIX **pi_com:**

```
SELECT count(distinct ?work)
WHERE
{
?work cdm:work_id_document ?id_document .
filter ( strStarts( str(?id_document),"pi_com" ) )
}
```

Resulting in ~2400 results. This is about right: there are 2025 Published initiatives on the BRP site.

# What are the distinct resource types of the pi_com works ? 

```
SELECT distinct ?resourceType
WHERE
{
?work cdm:work_id_document ?id_document .
?work cdm:work_has_resource-type ?resourceType
filter ( strStarts( str(?id_document),"pi_com" ) )
}
```

# Legal initiatives resource types 

rt:REG_DEL_DRAFT # Delegated Acts facet
rt:REG_DEL # Delegated Acts facet
rt:REG_IMPL_DRAFT # Implementing Acts facet
rt:IMPACT_ASSESS_INCEP # Legislative Proposals facet 
rt:DIR_DEL_DRAFT # Delegated Acts facet
rt:ROADMAP_EFC
rt:REG
rt:REG_DRAFT
rt:DIR_DRAFT
rt:OPIN_IMPACT_ASSESS
rt:DEC_IMPL_DRAFT # Implementing Acts facet
rt:ROADMAP
rt:DIR
rt:DIR_DEL # Delegated Acts facet
rt:DEC_DRAFT
rt:REG_IMPL # Implementing Acts facet
rt:DEC_IMPL # Implementing Acts facet
rt:DEC_DEL # Delegated Acts facet
rt:DIR_IMPL # Implementing Acts facet
rt:DEC
rt:DIR_IMPL_DRAFT # Implementing Acts facet
rt:IMPACT_ASSESS_SUM
rt:DEC_DEL_DRAFT # Delegated Acts facet
rt:IMPACT_ASSESS
rt:FACT_SUM_REPORT_CONSULT
rt:ACT
rt:DATPRO # this is a dummy when value is unknown
rt:CORRIGENDUM
rt:SWD
rt:EVL
rt:EVL_SUM_EXE
rt:COMMUNIC # Communication facet
rt:OPIN_EVL
rt:FC_SUM_EXE
rt:OPIN_FC
rt:FC

## Roadmaps (~425 in Feb 2021 )

rt:ROADMAP # valid 2009 - 2021
rt:ROADMAP_EFC # valid 2009 - 2021
rt:CFE_EVL_FC

## Inception impact assessment (~250 in Feb 2021)

rt:IMPACT_ASSESS_INCEP # valid 2009 - 2021
rt:CFE_IMPACT_ASSESS
rt:CFE_COMBINED 


# What are the distinct properties employed by the pi_com works

```
SELECT distinct ?p
WHERE
{
?work ?p [] .
?work cdm:work_id_document ?id_document .
filter ( strStarts( str(?id_document),"pi_com" ) )
}
```

# Legal initiatives properties employed

```
prefix cdm: <http://publications.europa.eu/ontology/cdm#>
prefix ann: <http://publications.europa.eu/ontology/annotation#>
prefix cmr: <http://publications.europa.eu/ontology/cdm/cmr#>
```

owl:sameAs
ann:build_info
cmr:creationDate  
cmr:lastModificationDate # fetch
cdm:date_creation_legacy
cdm:resource_legal_based_on_resource_legal # ?
cdm:resource_legal_id_sector # fetch
cdm:resource_legal_information_miscellaneous
cdm:work_created_by_agent # fetch
cdm:work_date_creation_legacy
cdm:work_date_document # fetch
cdm:work_has_resource-type # fetch
cdm:work_id_document # fetch
cdm:work_is_about_concept_eurovoc # fetch
cdm:work_drafted_in_language
cdm:resource_legal_has_type_act_concept_type_act # do not fetch (impact assesment, impact assesment summary)
cdm:resource_legal_id_celex
cdm:resource_legal_number_natural_celex
cdm:resource_legal_type 
cdm:resource_legal_year
cdm:work_embargo # fetch 
cdm:resource_legal_based_on_concept_treaty # fetch 
cdm:resource_legal_date_dispatch  # fetch 
cdm:resource_legal_is_about_concept_directory-code # fetch 
cdm:resource_legal_is_about_subject-matter # fetch 
cdm:work_cites_work  # ?
cdm:work_related_to_work # ?
cdm:resource_legal_service_responsible 
cdm:work_sequence # ?
cdm:work_title
cdm:work_version
cdm:work_part_of_dossier # fetch 
cdm:work_part_of_event_legal # ?
cdm:internal_number_sequential_number
cdm:internal_number_year
cdm:internal_number_prefix

# Legal initiatives are part of a dossier 

The *dossier* is a parent work (complex work) that probably contains all the works related to a legal initiative. Yes, there are multiple stages to a legal initiative, and at each stage other documents are added. 

```
select * 
{
 ?dossier cdm:dossier_contains_work ?work . 
}
```

OR  (hopefully the well implemented inverse)

```
select * 
{
 ?work cdm:work_part_of_dossier ?dossier  . 
}
```
 
# Open questions:
 
 Looking at the BRP website much information is available there that normally should be also found (should be recorded) in the Cellar somewhere. 
 
 The next questions arise
 
 * Where are the stages recorded ? (what CDM properties) 
 * Where are the feedback dates recorded (Feedback open from, Feedback closed by) ? (check date annotations in LAM)
 * What is the difference between *Type of act* and *Document category*
 
 