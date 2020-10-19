import json
import xlsxwriter
import pandas as pd
import re


def add_collections_info(eric_data, rd_data):
    bb_type = ["RD"]
    bb_data_cat = "MEDICAL RECORDS" # OR OTHER?


    #fill eric_data['eu_bbmri_eric_collections']
    #take oranis id info   eric_data['eu_bbmri_eric_biobanks'], look id up in   rd_data['rd_diseases']  = create id and have all infos together

    #rd_data['rd_diseases']['OrganizationID'] == ['11193']

    #eric_data['eu_bbmri_eric_collections']['id'] = biobankid + ':collection:' + name_disease
    #bbmri-eric:ID:IT_1382433386427702:collection:





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

def generate_id(eric_data, bb_id):

    id_list = ["rd_connect:ID:{0}:{1}".format(eric_data["eu_bbmri_eric_biobanks"]["country"].iloc[i],k) for i, k in enumerate(bb_id)]
    id_frame = pd.DataFrame(id_list)

    return id_frame

def add_biobank_info(eric_data, rd_data):


    bb_partner_cs = [False] # number of patients?
    contact_priority = [1] # positive integer

    bb_id = rd_data["rd_basic_info"]["OrganizationID"]
    bb_name = rd_data["rd_basic_info"]["name"]

    eric_data["eu_bbmri_eric_biobanks"]["country"] = get_country_code(eric_data, rd_data)
    eric_data["eu_bbmri_eric_biobanks"]["id"] = generate_id(eric_data, bb_id) 
    eric_data["eu_bbmri_eric_biobanks"]["name"] = bb_name


    eric_data["eu_bbmri_eric_biobanks"]["partner_charter_signed"] = pd.DataFrame(bb_partner_cs*len(eric_data["eu_bbmri_eric_biobanks"]))
    eric_data["eu_bbmri_eric_biobanks"]["contact_priority"] = pd.DataFrame(contact_priority*len(eric_data["eu_bbmri_eric_biobanks"]))

def add_persons(eric_data, rd_data):
    eric_data["eu_bbmri_eric_persons"]["id"] = rd_data["rd_contacts"]["ID"]
    eric_data["eu_bbmri_eric_persons"]["first_name"] = rd_data["rd_contacts"]["firstname"]
    eric_data["eu_bbmri_eric_persons"]["last_name"] = rd_data["rd_contacts"]["lastname"]
    eric_data["eu_bbmri_eric_persons"]["email"] = rd_data["rd_contacts"]["email"]
    eric_data["eu_bbmri_eric_persons"]["phone"] = rd_data["rd_contacts"]["phone"]
    
    bb_id = rd_data["rd_contacts"]["OrganizationID"]
    eric_data["eu_bbmri_eric_persons"]["biobanks"] = generate_id(eric_data, bb_id) 
    eric_data["eu_bbmri_eric_persons"]["country"] = [org_id_long.split(":")[-2] for org_id_long in eric_data["eu_bbmri_eric_persons"]["biobanks"]]


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

    write_excel(eric_data, eric_name)
