import json 
x = {
            "address": {
                "zip": "-",
                "country": "",
                "city": "-",
                "street1": "",
                "street2": "",
                "name of host institution": "-"
            },
            "diseases": [{
                    "number": "34",
                    "synonym": "17q12 microdeletion syndrome",
                    "gene": "HNF1B (HNF1 homeobox B) LHX1 (LIM homeobox 1)",
                    "omim": "#614527",
                    "name": "17q12 deletion",
                    "orphacode": "ORPHA261265",
                    "icd10": "Q93.5"
                }, {
                    "number": "26",
                    "synonym": "17q12 microduplication syndrome; Dup(17)(q12), Trisomy 17q12",
                    "gene": "",
                    "omim": "#614526",
                    "name": "17q12 duplication",
                    "orphacode": "ORPHA261272",
                    "icd10": "Q92.3"
                }
            ],
            "date of inclusion": "2015-01-07 10:12:44.744",
            "OrganizationID": 11193,
            "type": "registry",
            "url": ["https://connect.patientcrossroads.org/?org=17q12", "http://www.geisingeradmi.org/care-innovation/studies/17q12/"],
            "reg_quality": {
                "If_yes__specify": "",
                "Accreditation_certification_program": "[\"not specified\"]",
                "Training_program_for_the_registering_activities": "[\"not specified\"]",
                "Quality_control_external_audits": "[\"not specified\"]",
                "If_yes__frequency_of_audits": "",
                "Standardized_Operating_Procedures__SOPs__available_for_data_management": "[\"not specified\"]",
                "If_yes__specify__ISO_standards___": "",
                "Standardized_case-inclusion_and-exclusion_criteria": "[\"not specified\"]",
                "_fieldsDisplay": ""
            },
            "last activities": "2017-02-01 11:31:20.837",
            "core": {
                "Description": "The purpose of this registry is to gain a better understanding of the medical, developmental, and behavioral features associated with 17q12 deletions and duplications. The information provided by individuals and their families will help improve the diagnosis and clinical care for all those affected by this rare genetic variant.",
                "Additional_Imaging_available": "",
                "The_registry_biobanks_is_listed_in_other_inventories_networks": "[\"not specified\"]",
                "acronym": "",
                "Associated_data_available": "[\"Not specified\"]",
                "Type_of_host_institution": "",
                "Imaging_available": "[\"not specified\"]",
                "Ontologies": "[\"not specified\"]",
                "Additional_Associated_data_available": "",
                "Additional_Ontologies": "",
                "Source_of_funding": "[\"Foundation\"]",
                "Target_population_of_the_registry": "[\"National\"]",
                "Host_institution_is_a": "[\"Foundation\"]",
                "countryCode": "United States",
                "year_of_establishment": "",
                "Text5085": "",
                "Biomaterial_Available_in_biobanks": "",
                "Additional_networks_inventories": "",
                "_fieldsDisplay": "acronym_INSTANCE_thuk,Description_INSTANCE_qrsa,Host_institution_is_a_INSTANCE_kcrf,Type_of_host_institution_INSTANCE_brzu,Source_of_funding_INSTANCE_jgri,Text5085_INSTANCE_kilq,countryCode_INSTANCE_wxsv,Target_population_of_the_registry_INSTANCE_znhp,year_of_establishment_INSTANCE_qsai,Ontologies_INSTANCE_rdfk,Additional_Ontologies_INSTANCE_vftl,Associated_data_available_INSTANCE_ybag,Additional_Associated_data_available_INSTANCE_wahq,Imaging_available_INSTANCE_wjuz,Additional_Imaging_available_INSTANCE_hwyh,The_registry_biobanks_is_listed_in_other_inventories_networks_INSTANCE_cbyj,Additional_networks_inventories_INSTANCE_aego"
            },
            "reg_accessibility": {
                "Other1": "",
                "Available_Data": "[\"not specified\"]",
                "Has_the_registry_a_Data_Access_Committee_": "[\"not specified\"]",
                "Patient_s_data_linked_to_other_resources_": "[\"not specified\"]",
                "If_yes__please_provide_the_Data_Access_Committee_webpage": "",
                "Select9246": "[\"not specified\"]",
                "Personal_Data_Collected": "[\"not specified\"]",
                "Data_Access_Agreement": "",
                "Is_an_ethics_board_decision_already_available_for_the_use_of_the_samples_in_research": "[\"not specified\"]",
                "Do_you_use_a_Data_Access_Agreement_": "[\"not specified\"]",
                "Type_of_consent_is_obtained_from_the_patients": "[\"not specified\"]",
                "Specific_procedure_for_access_to_raw_data": "[\"not specified\"]",
                "Other4838": "",
                "_fieldsDisplay": ""
            },
            "main contact": {
                "last name": "Mitchel",
                "first name": "Marissa",
                "email": "mwmitchel@geisinger.edu"
            },
            "name": "17q12 Interest Group registry",
            "ID": "http://catalogue.rd-connect.eu/apiv1/regbb/organization-id/11193",
            "contacts": {
                "last name": "Mitchel",
                "first name": "Marissa",
                "email": "mwmitchel@geisinger.edu"
            }
        }


print(type(x))
#y = json.loads(x)

print(x["name"]) 