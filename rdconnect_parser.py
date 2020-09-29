import json
import xlsxwriter

def prep_packages(workbook, package_name):

    packages = workbook.add_worksheet("packages")

    packages.write("A1", "name")
    packages.write("B1", "label")
    packages.write("C1", "description")
    packages.write("D1", "tags")

    packages.write("A2", package_name)
    packages.write("B2", package_name)
    packages.write("C2", "RD-Connect Auto Test")

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

    entities.write("A2", entity_names[0])
    entities.write("B2", package_name)
    entities.write("C2", "Directory")
    entities.write("G2", "PostgreSQL")

    entities.write("A3", entity_names[1])
    entities.write("B3", package_name)
    entities.write("C3", "Directory")
    entities.write("G3", "PostgreSQL")

    return entities

def prep_attributes(workbook):

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


    return attributes


if __name__ == "__main__":

    package_name = "rd_connect_test"
    entity_names = ["directories", "deseases"]

    entity_full_names = [package_name + "_" + e for e in entity_names]

    workbook = xlsxwriter.Workbook("rd_connect_auto.xlsx")


    packages = prep_packages(workbook, package_name)
    entities = prep_entities(workbook, package_name, entity_names)
    attributes = prep_attributes(workbook)

    # test_dir holds data of biobanks/registries
    rd_connect_test_dir = workbook.add_worksheet(entity_full_names[0])
    rd_connect_test_des = workbook.add_worksheet(entity_full_names[1])

    with open("rdconnectfinder.json") as f:
        file = dict(json.load(f))


    first = True
    row = 1
    col = 0
    key_list = []
    entry_types = ["string", "int"]
    current_type = entry_types[0]
    entry_num = 1
    print("LEN: ", len(file[list(file.keys())[0]]))

    for j_entry in file[list(file.keys())[0]]:
        for key in j_entry.keys():
            entry_type = type(j_entry[key])

            content = j_entry[key]
            key = key.replace(" ", "_")

            if entry_type == type(1):
                current_type = entry_types[1]
            else:
                current_type = entry_types[0]
            if entry_type == type(dict()) or entry_type == type(list()):
                continue

            else:
                if not key in key_list:
                    key_list.append(key)
                    attributes.write(len(key_list), 0, key)
                    attributes.write(len(key_list), 1, key)
                    attributes.write(len(key_list), 3, entity_names[0])
                    attributes.write(len(key_list), 4, current_type)
                    attributes.write(len(key_list), 6, "FALSE")
                    attributes.write(len(key_list), 7, "FALSE")
                    attributes.write(len(key_list), 9, "FALSE")

                    # if not entry_type == type(1):
                    #     attributes.write(len(key_list), 9, "AUTO")
                    if key == "OrganizationID":
                        attributes.write(len(key_list), 9, "TRUE")

                    rd_connect_test_dir.write(0, len(key_list)-1, key)
                
                if key_list.index(key) in [0, 3]:
                    content = content.split(" ")[0]
                    content = content.replace("-", "_")
                    content = int(content)

                rd_connect_test_dir.write(entry_num, key_list.index(key), content)
        entry_num += 1

    print("entries: ", entry_num)
    workbook.close()
 