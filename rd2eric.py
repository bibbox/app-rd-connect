import json
import xlsxwriter
import pandas as pd
import re


def add_collections_info(eric_data, rd_data):
    bb_type = ["RD"]
    bb_data_cat = "MEDICAL RECORDS" # OR OTHER?

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

    print(id_frame)
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

    print(eric_data["eu_bbmri_eric_biobanks"])


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

    write_excel(eric_data, eric_name)
