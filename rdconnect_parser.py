import json
import xlsxwriter
import pandas as pd
import template_xlsx
import string
import helper_functions



def add_basic_info(workbook, data, package_name, entity_name, key, content, entry_num):

    print("add basic info of: ", key)


def parse_data(package_name, workbook_name):

    workbook, entities = helper_functions.create_template(package_name, workbook_name)
    workbook.close()

    df_list = []
    xls = pd.ExcelFile(workbook_name)
    for sheet_name in xls.sheet_names:
        df_list.append(pd.read_excel(xls, sheet_name))
    
    [print(df) for df in df_list]

    return df_list, entities

if __name__ == "__main__":

    package_name = "rd"
    workbook_name = "rd_connect_auto.xlsx"
    data = pd.read_excel("rd_connect_entity_info.xlsx")
    # print(data)

    # workbook, entities = template_xlsx.create_template(package_name, workbook_name)

    # with open("rdconnectfinder.json") as f:
    #     file = dict(json.load(f))

    df_list, entitities = parse_data(package_name, workbook_name)

    # first = True
    # row = 1
    # col = 0
    # key_list = []
    # all_keys = []
    # entry_types = ["string", "int"]
    # current_type = entry_types[0]
    # entry_num = 1
    # all_data = file[list(file.keys())[0]]

    # for j_entry in all_data:
    #     for key in j_entry.keys():
    #         entry_type = type(j_entry[key])
    #         # print(entry_type)
    #         all_keys.append(key)

    #         content = j_entry[key]
    #         # INT or STRING else Skip
    #         if isinstance(j_entry[key], int) or isinstance(j_entry[key], str):
    #             add_basic_info(workbook, data, package_name, "basic_info", key, content, entry_num)

    #         if entry_type == type(dict()) or entry_type == type(list()):
    #             continue


    #     entry_num += 1

    # print("entries: ", entry_num)
    # print(set(all_keys))
    # workbook.close()


    #loook for special characters
    import re
    # print("entries: ", entry_num)
    # print(set(all_keys))
    # workbook.close()

    invalidChars = set(string.punctuation.replace("_", " "))


    file = workbook_name  #workbook_name[:-5] + '_template.xlsx'
    #print('filename: ',file)

        #for entity in entities:
        for sheet_name in xls.sheet_names:

            df1 = pd.read_excel(xls, sheet_name)

            #print("Validdd" if re.match("^[a-zA-Z0-9_]*$", sheet_name) else "Invaliddd")

            if not re.match("^[a-zA-Z0-9 _]*$", sheet_name):
                for char in invalidChars:
                    sheet_name = sheet_name.replace(char,'_')
                print(sheet_name)

            for sheet_key in df1.keys():
                if not re.match("^[a-zA-Z0-9_]*$", sheet_key):
                    print(sheet_key)




            # if any(char in invalidChars for char in sheet_name):


    with pd.ExcelWriter('emx_rdconnect_test.xlsx') as writer:
        for k, df1 in enumerate(df_list):
            
            sheet_name = package_name + "_" + entitities[k]
            df1.to_excel(writer, sheet_name=sheet_name,index=False)








        # with pd.ExcelWriter('emx_rdconnect_test.xlsx') as writer:
        #     df1.to_excel(writer,full_entity_name)
        # print(df1)

   

    # sheet_to_df_map = {}
    # for sheet_name in xls.sheet_names:
    #     sheet_to_df_map[sheet_name] = xls.parse(sheet_name)



        
