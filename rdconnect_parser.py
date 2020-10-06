import json
import xlsxwriter
import pandas as pd
import helper_functions
import string



def add_basic_info(df_dict, data, package_name, entity_name, key, content, entry_num):

    print("add basic info of: ", key)
    print(df_dict[package_name + "_" + entity_name])



def parse_data(package_name, workbook_name):

    workbook, entities = helper_functions.create_template(package_name, workbook_name)
    workbook.close()

    df_dict = {}
    xls = pd.ExcelFile(workbook_name)
    for sheet_name in xls.sheet_names:
        df_dict[sheet_name] = pd.read_excel(xls, sheet_name)
    
    [print(df) for df in df_dict]

    return df_dict, entities

if __name__ == "__main__":

    package_name = "rd"
    workbook_name = "rd_connect_auto.xlsx"
    data = pd.read_excel("rd_connect_entity_info.xlsx")
    # print(data)

    workbook, entities = helper_functions.create_template(package_name, workbook_name)

    with open("rdconnectfinder.json") as f:
        file = dict(json.load(f))

    df_dict, entitities = parse_data(package_name, workbook_name)

    first = True
    row = 1
    col = 0
    key_list = []
    all_keys = []
    entry_types = ["string", "int"]
    current_type = entry_types[0]
    entry_num = 1
    all_data = file[list(file.keys())[0]]

    for j_entry in all_data:
        for key in j_entry.keys():
            entry_type = type(j_entry[key])
            # print(entry_type)
            all_keys.append(key)

            content = j_entry[key]
            # INT or STRING else Skip
            if isinstance(j_entry[key], int) or isinstance(j_entry[key], str):
                add_basic_info(df_dict, data, package_name, "basic_info", key, content, entry_num)

            if entry_type == type(dict()) or entry_type == type(list()):
                continue


        entry_num += 1

    # print("entries: ", entry_num)
    # print(set(all_keys))
    workbook.close()


    # helper_functions.anjas_function(df_list, entities)
