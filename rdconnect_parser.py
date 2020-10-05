import json
import xlsxwriter
import pandas as pd
import template_xlsx


def add_basic_info(workbook, data, package_name, entity_name, key, content, entry_num):

    print("add basic info of: ", key)
    sheet = workbook.get_worksheet_by_name(package_name + "_" + entity_name)
    column = list(data.attribute[data.entity.values == entity_name]).index(key)
    sheet.write(entry_num, column, content)

if __name__ == "__main__":

    package_name = "rd"
    workbook_name = "rd_connect_auto.xlsx"
    data = pd.read_excel("rd_connect_entity_info.xlsx")
    print(data)


    workbook, entities = template_xlsx.create_template(package_name, workbook_name)

    with open("rdconnectfinder.json") as f:
        file = dict(json.load(f))


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
                add_basic_info(workbook, data, package_name, "basic_info", key, content, entry_num)

            if entry_type == type(dict()) or entry_type == type(list()):
                continue


        entry_num += 1

    print("entries: ", entry_num)
    print(set(all_keys))
    workbook.close()


    #change signs

    #print(entities)
    
    file = workbook_name  #workbook_name[:-5] + '_template.xlsx'
    #print('filename: ',file)
    xls = pd.ExcelFile(file)

    for entity in entities:
        print(entity)
        full_entity_name = package_name + "_" + entity
        df1 = pd.read_excel(xls, full_entity_name)
        print(df1)
