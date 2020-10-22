import json
import xlsxwriter
import pandas as pd
import re
import numpy as np


def add_collections_info(eric_data, rd_data):
    bb_type = ["RD"]
    bb_data_cat = "MEDICAL RECORDS" # OR OTHER?

    print(eric_data["eu_bbmri_eric_biobanks"])

    biobank_ids = eric_data["eu_bbmri_eric_biobanks"]['id']
    #orga_ids = biobank_id.str.split(pat=":")    #int(orga_id[-1])
    ids = [] 

    count = 0
    for biobank_id in biobank_ids:
        m = rd_data['rd_diseases']['OrganizationID'] == int(biobank_id.split(':')[-1])
        rows = rd_data['rd_diseases'][m]
        #a = pd.concat([a,list(biobank_id + ':collection:' +rows['name'])])
        for enum,name in enumerate(rows['name'].values):
            ids.append(str(biobank_id) + ':collection:' +str(name))
            eric_data['eu_bbmri_eric_collections'].at[count,'id'] = str(biobank_id) + ':collection:' + str(enum+1) + ":" + str(name)
            #split_id = str(str(biobank_id) + ':collection:' +str(r)).str.split(pat=":")
            eric_data['eu_bbmri_eric_collections'].at[count,'country']  = biobank_id.split(':')[2]
            eric_data['eu_bbmri_eric_collections'].at[count,'biobank']  = str(biobank_id)
            eric_data['eu_bbmri_eric_collections'].at[count,'name']  = str(name)

            eric_data['eu_bbmri_eric_collections'].at[count,'order_of_magnitude'] = int(np.log10(np.max([1, rows.reset_index(drop=True).at[enum,'number']])))
            eric_data['eu_bbmri_eric_collections'].at[count,'size'] = rows.reset_index(drop=True).at[enum,'number']

            eric_data['eu_bbmri_eric_collections'].at[count,'type'] = 'RD'
            eric_data['eu_bbmri_eric_collections'].at[count,'contact_priority'] = 5


            rd_org_id = rd_data['rd_basic_info']['OrganizationID'] == int(biobank_id.split(':')[-1])
            if "biobank" in rd_data["rd_basic_info"]["type"][rd_org_id].values[0]:
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = "BIOLOGICAL_SAMPLES,OTHER"

            elif "registry" in rd_data["rd_basic_info"]["type"][rd_org_id].values[0]:
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = "MEDICAL_RECORDS,OTHER"
            else:
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = "OTHER"

            count +=1


    # for k, id_ in enumerate(ids):
    #     eric_data['eu_bbmri_eric_collections'].at[k,'id']  = id_

    # splits_ids = eric_data['eu_bbmri_eric_collections']['id'].str.split(pat=":")     

    # for k, split_id in enumerate(splits_ids):
    #     eric_data['eu_bbmri_eric_collections'].at[k,'country']  = split_id[2]
    #     eric_data['eu_bbmri_eric_collections'].at[k,'biobank']  = split_id[0] +':'+split_id[1] +':'+split_id[2] +':'+split_id[3]
    #     eric_data['eu_bbmri_eric_collections'].at[k,'name']  = split_id[5]



    #fill eric_data['eu_bbmri_eric_collections']
    #take oranis id info   eric_data['eu_bbmri_eric_biobanks'], look id up in   rd_data['rd_diseases']  = create id and have all infos together

    #rd_data['rd_diseases']['OrganizationID'] == '11193'

    #eric_data['eu_bbmri_eric_collections']['id'] = biobankid + ':collection:' + name_disease
    #bbmri-eric:ID:IT_1382433386427702:collection:

     


    print(eric_data["eu_bbmri_eric_collections"])





def get_country_code(eric_data, rd_data):
    bb_country = rd_data["rd_address"]["country"]
    codes = list(eric_data["eu_bbmri_eric_countries"]["name"].values)

    code_frame = bb_country

    for k, country in enumerate(bb_country):
        if country in codes:
            code_frame.iloc[k] = eric_data["eu_bbmri_eric_countries"]["id"][eric_data["eu_bbmri_eric_countries"]["name"] == country].values[0]
        else:
            code_frame.iloc[k] = "ZZ"

    return code_frame

def generate_bb_id(eric_data, bb_id):

    id_list = ["rd_connect:ID:{0}:{1}".format(eric_data["eu_bbmri_eric_biobanks"]["country"].iloc[i],k) for i, k in enumerate(bb_id)]
    id_frame = pd.DataFrame(id_list)

    return id_frame

def add_biobank_info(eric_data, rd_data):

    # add MANDATORY information:
    bb_partner_cs = [False] # number of patients?
    contact_priority = [1] # positive integer

    bb_id = rd_data["rd_basic_info"]["OrganizationID"]
    bb_name = rd_data["rd_basic_info"]["name"]
    juridical = rd_data["rd_address"]["nameofhostinstitution"]

    eric_data["eu_bbmri_eric_biobanks"]["country"] = get_country_code(eric_data, rd_data)
    eric_data["eu_bbmri_eric_biobanks"]["id"] = generate_bb_id(eric_data, bb_id) 
    eric_data["eu_bbmri_eric_biobanks"]["name"] = bb_name
    eric_data["eu_bbmri_eric_biobanks"]["juridical_person"] = juridical

    eric_data["eu_bbmri_eric_biobanks"]["juridical_person"][pd.isnull(juridical)] = "not specified"

    eric_data["eu_bbmri_eric_biobanks"]["partner_charter_signed"] = pd.DataFrame(bb_partner_cs*len(eric_data["eu_bbmri_eric_biobanks"]))
    eric_data["eu_bbmri_eric_biobanks"]["contact_priority"] = pd.DataFrame(contact_priority*len(eric_data["eu_bbmri_eric_biobanks"]))

def additional_biobank_info(eric_data, rd_data):

    # add additional information:
    for biobank in eric_data["eu_bbmri_eric_biobanks"]["id"]:
        rd_id = int(biobank.split(":")[-1])
        description = rd_data["rd_core"]["Description"][rd_data["rd_core"]["OrganizationID"] == rd_id].values
        acronym = rd_data["rd_core"]["acronym"][rd_data["rd_core"]["OrganizationID"] == rd_id].values

        if biobank in eric_data["eu_bbmri_eric_persons"]["biobanks"].values:
            person_id = eric_data["eu_bbmri_eric_persons"]["id"][eric_data["eu_bbmri_eric_persons"]["biobanks"] == biobank].values
            eric_data["eu_bbmri_eric_biobanks"]["contact"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = person_id

        if pd.isnull(description) and biobank in rd_data["rd_bb_core"]["OrganizationID"].values:
            description = rd_data["rd_bb_core"]["Description"][rd_data["rd_bb_core"]["OrganizationID"] == rd_id].values

        if pd.isnull(acronym) and biobank in rd_data["rd_bb_core"]["OrganizationID"].values:
            acronym = rd_data["rd_core"]["acronym"][rd_data["rd_core"]["OrganizationID"] == rd_id].values


        eric_data["eu_bbmri_eric_biobanks"]["description"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = description
        eric_data["eu_bbmri_eric_biobanks"]["acronym"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = acronym


    # eric_data["eu_bbmri_eric_biobanks"]["acronym"] = rd_data["rd_basic_info"]["name"]

def generate_contact_id(eric_data):

    id_list = ["rd_connect:contactID:{0}_{1}".format(x.split(":")[2], k) for k, x in enumerate(eric_data["eu_bbmri_eric_persons"]["biobanks"])]
    id_frame = pd.DataFrame(id_list)

    return id_frame


def add_persons(eric_data, rd_data):
    eric_data["eu_bbmri_eric_persons"]["first_name"] = rd_data["rd_contacts"]["firstname"]
    eric_data["eu_bbmri_eric_persons"]["last_name"] = rd_data["rd_contacts"]["lastname"]
    eric_data["eu_bbmri_eric_persons"]["email"] = rd_data["rd_contacts"]["email"]
    eric_data["eu_bbmri_eric_persons"]["phone"] = rd_data["rd_contacts"]["phone"]
    
    bb_id = rd_data["rd_contacts"]["OrganizationID"]
    eric_data["eu_bbmri_eric_persons"]["biobanks"] = generate_bb_id(eric_data, bb_id) 
    eric_data["eu_bbmri_eric_persons"]["country"] = [org_id_long.split(":")[-2] for org_id_long in eric_data["eu_bbmri_eric_persons"]["biobanks"]]

    eric_data["eu_bbmri_eric_persons"]["id"] = generate_contact_id(eric_data)


def write_excel(eric_data, eric_name):
    
    with pd.ExcelWriter(eric_name.split(".xlsx")[0]+"_merged"+".xlsx",engine='xlsxwriter') as writer:
        for sheet_name in eric_data.keys():
            df1 = eric_data[sheet_name]
            df1.to_excel(writer, sheet_name=sheet_name,index=False)


if __name__ == "__main__":
    eric_name = "rd2eric.xlsx"
    rd_name = "rd_connect.xlsx"

    rd_data = pd.read_excel(rd_name, sheet_name=None)
    eric_data = pd.read_excel(eric_name, sheet_name=None)

    add_biobank_info(eric_data, rd_data)
    add_collections_info(eric_data, rd_data)
    add_persons(eric_data, rd_data)

    additional_biobank_info(eric_data, rd_data)

    write_excel(eric_data, eric_name)
