import json
import xlsxwriter
import pandas

def prep_package(workbook, package_name):
    packages = workbook.add_worksheet("packages")

    packages.write("A1", "name")
    packages.write("A1", "name")
    packages.write("B1", "label")
    packages.write("C1", "description")
    packages.write("D1", "tags")

    packages.write("A2", package_name)
    packages.write("B2", package_name)
    packages.write("C2", "RD-Connect Auto Template")

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
        entities.write(k+1, 2 , "Directory")
        entities.write(k+1, 6 , "PostgreSQL")

    return entities

def prep_attributes(workbook, package_name, data):

    attrs = list(data["Sheet1"].iloc[1:]["attribute"].values)
    ent_list = list(data["Sheet1"].iloc[1:]["entity"].values)
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

        if attr == "OrganizationID" or attr[:2] == "ID":
            attributes.write(k+1, 7, "true")
            attributes.write(k+1, 9, "true")


    return attributes

def add_attributes(sheet, data, entity):

    attributes = list(data["Sheet1"].iloc[1:]["attribute"][data["Sheet1"].iloc[1:]["entity"] == entity])

    for k, attr in enumerate(attributes):
        sheet.write(0, k, attr)


def create_template(package_name, workbook_name):

    workbook = xlsxwriter.Workbook(workbook_name)

    data = pandas.read_excel("rd_connect_entity_info.xlsx", sheet_name=None)
    entities = list(set(data["Sheet1"].iloc[1:]["entity"].values))
    entities = sorted([ent for ent in entities if type(ent) == type("string")])
    attributes = list(set(data["Sheet1"].iloc[1:]["attribute"].values))

    packages_sheet = prep_package(workbook, package_name)
    entities_sheet = prep_entities(workbook, package_name, entities)
    attributes_sheet = prep_attributes(workbook, package_name, data)

    for entity in entities:
        full_entity_name = package_name + "_" + entity
        sheet = workbook.add_worksheet(full_entity_name)
        add_attributes(sheet, data, entity)

    return workbook, entities

if __name__ == "__main__":
    package_name = "rd"
    workbook_name = "rd_connect_auto_template.xlsx"

    workbook, entities = create_template(package_name, workbook_name)

    workbook.close()

