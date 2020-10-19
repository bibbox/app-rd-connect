import json
import xlsxwriter
import pandas as pd
import re

def prep_package(workbook, package_name, workbook_name):
    packages = workbook.add_worksheet("packages")
    label = workbook_name.split(".")[0]

    packages.write("A1", "name")
    packages.write("A1", "name")
    packages.write("B1", "label")
    packages.write("C1", "description")
    packages.write("D1", "tags")

    packages.write("A2", package_name)
    packages.write("B2", package_name)
    packages.write("C2", label)

    return packages

def prep_entities(workbook, package_name, entity_names):

    entities = workbook.add_worksheet("entities")

    entities.write("A1", "name")
    entities.write("B1", "package")
    entities.write("C1", "label")
    entities.write("D1", "description")
    entities.write("E1", "abstract")
    entities.write("F1", "extends")
    entities.write("G1", "backend")
    entities.write("H1", "tags")
    entities.write("I1", "label-en")
    entities.write("J1", "description-en")

    for k, ent in enumerate(entity_names):
        entities.write(k+1, 0 , ent)
        entities.write(k+1, 1 , package_name)
        entities.write(k+1, 2 , ent)
        entities.write(k+1, 6 , "PostgreSQL")

    return entities

def prep_attributes(workbook, package_name, data):

    # add datatype "text" for longer fields:
    longer_fields = ["_fieldsDisplay", "name", "Description", "If_yes__specify", "If_not__please_specify_what_type_of_collections_can_be_publicly_available", 
                    "Standardized_Operating_Procedures__SOPs__available_for_data_management"]

    attrs = list(data["Sheet1"].iloc[0:]["attribute"].values)
    ent_list = list(data["Sheet1"].iloc[0:]["entity"].values)
    attributes = workbook.add_worksheet("attributes")

    attributes.write("A1", "name")
    attributes.write("B1", "label")
    attributes.write("C1", "description")
    attributes.write("D1", "entity")
    attributes.write("E1", "dataType")
    attributes.write("F1", "refEntity")
    attributes.write("G1", "nillable")
    attributes.write("H1", "unique")
    attributes.write("I1", "visible")
    attributes.write("J1", "idAttribute")
    attributes.write("K1", "labelAttribute")
    attributes.write("L1", "label-en")
    attributes.write("M1", "description-en")

    for k, attr in enumerate(attrs):
        ent = package_name + "_" + ent_list[k]
        attributes.write(k+1, 0 , attr)
        attributes.write(k+1, 1 , attr)
        attributes.write(k+1, 2 , " ")
        attributes.write(k+1, 3 , ent)
        attributes.write(k+1, 7, "false")

        if ent_list[k] == "basic_info" and attr == "OrganizationID" or ent_list[k] != "basic_info" and attr[:2] == "ID":
            attributes.write(k+1, 4, "int")

            attributes.write(k+1, 7, "true")
            attributes.write(k+1, 9, "true")

        if attr in longer_fields:
            attributes.write(k+1, 4, "text")


    return attributes

def add_attributes(sheet, data, entity):

    attributes = list(data["Sheet1"]["attribute"][data["Sheet1"]["entity"] == entity])

    for k, attr in enumerate(attributes):
        sheet.write(0, k, attr)


def create_template(package_name, workbook_name):

    workbook = xlsxwriter.Workbook(workbook_name)

    data = pd.read_excel("rd_connect_entity_info.xlsx", sheet_name=None)
    
    entities = list(set(data["Sheet1"].iloc[1:]["entity"].values))
    entities = sorted([ent for ent in entities if type(ent) == type("string")])
    attributes = list(set(data["Sheet1"].iloc[1:]["attribute"].values))

    packages_sheet = prep_package(workbook, package_name, workbook_name)
    entities_sheet = prep_entities(workbook, package_name, entities)
    attributes_sheet = prep_attributes(workbook, package_name, data)

    for entity in entities:
        full_entity_name = package_name + "_" + entity
        sheet = workbook.add_worksheet(full_entity_name)
        add_attributes(sheet, data, entity)

    return workbook, entities


def remove_double_contacts(df_dict):

    # get indices of non-duplicates
    keep_indices = df_dict["rd_contacts"].iloc[:, [0,2,3,4,5]].drop_duplicates().index
    
    # get subset of non-duplicates and reset indices
    df_contacts = df_dict["rd_contacts"].iloc[list(keep_indices)].reset_index(drop=True)
    
    # reset "ID" column
    df_contacts["ID"] = list(df_contacts.index)

    df_dict["rd_contacts"] = df_contacts

def make_clean_EMX(df_dict, clean_EMX = 'emx_rdconnect_test.xlsx'):
    ''' removes special characters
    for sheets and header only a-z,A-Z,0-9,-,_ allowed
    for data  only a-z,A-Z,0-9,#,_ allowed
    
    input:
    df_dict: dict of all sheets (entities + data)
    clean_EMX: name of output file ready for molgenis
    
    output:
    create clean EMX file with name choosen for clean_EMX'''

    #output file is created, than iterate through all sheets and set allowed chars, delete unallowed ones
    remove_double_contacts(df_dict)

    with pd.ExcelWriter(clean_EMX,engine='xlsxwriter') as writer:
        for sheet_name in df_dict.keys():

            df1 = df_dict[sheet_name]

            if sheet_name == 'entities':
                df1['name']=  pd.Series([re.sub('[^A-Za-z0-9_-]+', '',dd) for dd in df1['name']])
            if sheet_name == 'attributes':    
                df1['name']=  pd.Series([re.sub('[^A-Za-z0-9_]+', '',dd) for dd in df1['name']])
                df1['entity']=  pd.Series([re.sub('[^A-Za-z0-9_-]+', '',dd) for dd in df1['entity']])


            if not re.match('[^A-Za-z0-9_-]+', sheet_name):
                sheet_name_new = re.sub('[^A-Za-z0-9_-]+', '', sheet_name)
                

            for sheet_key in df1.keys():

                sheet_key_new = re.sub('[^A-Za-z0-9_-]+', '', sheet_key)
                df1[sheet_key_new] = df1.pop(sheet_key)

                

            df1.to_excel(writer, sheet_name=sheet_name_new,index=False)





if __name__ == "__main__":
    package_name = "rd"
    workbook_name = "rd_connect_auto_template.xlsx"

    workbook, entities = create_template(package_name, workbook_name)

    workbook.close()

