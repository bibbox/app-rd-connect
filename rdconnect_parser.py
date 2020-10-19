import json
import xlsxwriter
import pandas as pd
import helper_functions
import string
import re



def add_basic_info(df_dict, package_name, entity_name, key, content):

    # get correct dataframe
    df = df_dict[package_name + "_" + entity_name]

    df.at[len(df[key].dropna()), key] = content

def add_multi_content(df_dict, package_name, entity_name, key, list_like, org_id):

    # handle main contact
    main = "false"
    if "main" in key:
        key = "contacts"
        main = "true"

    try:
        df = df_dict[package_name + "_" + key]
        
        # list_like: URL, DISEASES
        if isinstance(list_like, list):
            # check/add URL(S):
            if len(list_like) > 0 and isinstance(list_like[0], str):
                for url in list_like:
                    df.at[len(df["OrganizationID"].dropna()), "OrganizationID"] = org_id
                    df.at[len(df[key].dropna()), key] = url
                    df.at[len(df["ID"].dropna()), "ID"] = len(df["ID"])

            # check/add DISEASE(S)
            if len(list_like) > 0 and isinstance(list_like[0], dict):

                for entry in list_like:
                    for k in entry.keys():
                        if len(entry[k]) > 255:
                            content = "none"
                        else:
                            content = re.sub('[^A-Za-z0-9_@. ]+', '',entry[k])
                        
                        df.at[len(df[k].dropna()), k] = content

                    df.at[len(df["OrganizationID"].dropna()), "OrganizationID"] = org_id
                    df.at[len(df["ID"].dropna()), "ID"] = len(df["ID"])


        # add address or contact
        if list_like and  isinstance(list_like, dict):
            df.at[len(df["OrganizationID"].dropna()), "OrganizationID"] = org_id

            df.at[len(df["ID"].dropna()), "ID"] = len(df["ID"])

            for k in list_like.keys():

                if "contact" in key:
                    df.at[len(df[k].dropna()), "main"] = main


                    
                content = re.sub('[^A-Za-z0-9_@. ]+', '',list_like[k])


                df.at[len(df[k].dropna()), k] = content





    except KeyError as e:
        print("KEY ERROR: ", e)
        pass


def parse_data(package_name, workbook_name):

    workbook, entities = helper_functions.create_template(package_name, workbook_name)
    workbook.close()

    df_dict = {}
    xls = pd.ExcelFile(workbook_name)
    for sheet_name in xls.sheet_names:
        df_dict[sheet_name] = pd.read_excel(xls, sheet_name)
    
    return df_dict, entities

if __name__ == "__main__":

    package_name = "rd"
    workbook_name = "rd_connect.xlsx"
    workbook, entities = helper_functions.create_template(package_name, workbook_name)

    with open("rdconnectfinder.json") as f:
        file = dict(json.load(f))

    df_dict, entitities = parse_data(package_name, workbook_name)

    entry_types = ["string", "int"]
    all_data = file[list(file.keys())[0]]

    for j_entry in all_data:
        for key in j_entry.keys():
            entry_type = type(j_entry[key])
            org_id = j_entry["OrganizationID"]

            content = j_entry[key]
            # INT or STRING for basic info
            if isinstance(j_entry[key], int) or isinstance(j_entry[key], str):
                add_basic_info(df_dict, package_name, "basic_info", key, content)

            # DICT or LIST for other types of entities
            if entry_type == type(dict()) or entry_type == type(list()):
                add_multi_content(df_dict, package_name, j_entry[key], key, content, org_id)
                continue

    workbook.close()


    helper_functions.make_clean_EMX(df_dict, workbook_name)
