import json
import xlsxwriter
import pandas as pd
import re
import numpy as np
import geopy


def add_code_to_types(eric_data, code, code_id, name):
    """ adds icd10 or orpha code to "bbmri_eric_disease_type",
        generates url from code, adds "ontology": orphanet or ICD-10

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    code : string
        icd10 or orpha code eg.: ORPHA:166 or G60.0
    code_id : string
        unique code id for disease code eg.: "ORPHA:166" or "urn:miriam:icd:G60.0"
    name : string
        name of disease from rd_connect
    """

    index = eric_data['eu_bbmri_eric_disease_types'].index.max()+1
    ontology = "orphanet"
    url = "http://identifiers.org/icd/{0}".format(code_id)
    if not "ORPHA" in code:
        ontology = "ICD-10"
        url = "https://identifiers.org/{0}".format(code_id)


    eric_data['eu_bbmri_eric_disease_types'].at[index, "id"] = code_id
    eric_data['eu_bbmri_eric_disease_types'].at[index, "code"] = code
    eric_data['eu_bbmri_eric_disease_types'].at[index, "label"] = name
    eric_data['eu_bbmri_eric_disease_types'].at[index, "ontology"] = ontology
    eric_data['eu_bbmri_eric_disease_types'].at[index, "uri"] = url


def check_disease_type(eric_data, rd_data, enum, name, rows, count):
    """ checks param "diagnosis_available" for icd10 or orpha - codes.
        if codes can be extracted and not in bbmri_eric_disease_types:
        calls function: add_code_to_types

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    rd_data : dict
        dictionary that holds rd_connect information (with EMX package/entity/attribute names)
    enum : int
        row number of current disease in rd_connect
    name : string
        name of disease from rd_connect
    rows : data frame
        data frame holding disease information of current biobank
    count : int
        counter of current (sub) collection. needed for access to "diagnosis_available"

    Returns
    -------
    list of strings
        list of codes
    """


    icd_code = rows.reset_index(drop=True).at[enum,'icd10']
    orpha_code = rows.reset_index(drop=True).at[enum,'orphacode']
    code_frame = eric_data['eu_bbmri_eric_disease_types']['code'].values
    code_list = []

    if pd.isnull(icd_code) and pd.isnull(orpha_code):
        return code_list

    if not pd.isnull(orpha_code):
        orpha_codes = ["ORPHA:" + orph for orph in re.findall(r'\d+', orpha_code)]
        # print("before list comp: \n", orpha_code)
        # print("\n after: \n ", orpha_codes)
        for code in orpha_codes:
            code = code.replace(" ", "")
            if code in code_frame:
                code_list.append(str(code))
            else:
                code_id = code
                add_code_to_types(eric_data, code, code_id, name)

        # make sure that codes occur only once
        code_list = sorted(list(set(code_list)))
        eric_data['eu_bbmri_eric_collections'].at[count,'diagnosis_available'] = ",".join(code_list)

    if not pd.isnull(icd_code):
        icd_no_space = icd_code.replace(" ", "")
        letter_positions = [m.span() for m in re.finditer(r'[^A-Za-z]+', icd_no_space)]
        icd_codes = [icd_no_space[k[0]-1] + icd_no_space[k[0]:k[1]] for k in letter_positions]

        code_list = []
        rex = re.compile("^[A-Z]{1}[0-9]{2}[.][0-9]{1}$")
        for code in icd_codes:
            code = code.replace(" ", "")
            if code in code_frame:
                code_list.append("urn:miriam:icd:"+str(code))

            else:
                if rex.match(code):
                    code_id = "urn:miriam:icd:"+str(code)
                    add_code_to_types(eric_data, code, code_id, name)

        # make sure that codes occur only once
        code_list = sorted(list(set(code_list)))
        eric_data['eu_bbmri_eric_collections'].at[count,'diagnosis_available'] = ",".join(code_list)

        return code_list

def get_material_type(eric_data, rd_materials):
    """[summary]

    Parameters
    ----------
    eric_data : [type]
        [description]
    rd_materials : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    
    eric_types = eric_data["eu_bbmri_eric_material_types"]["id"].values
    rd_material_upper = rd_materials.values[0].upper()
    rd_material_underline = rd_material_upper.replace(" ", "_")
    found_materials = []

    for type_ in eric_types:
        if type_ in rd_material_upper:
            found_materials.append(type_)
        if type_ in rd_material_underline:
            found_materials.append(type_)
        if "TISSUES" in rd_material_upper:
            found_materials.append("TISSUE_PARAFFIN_EMBEDDED")


    if len(found_materials) > 0:
        found = ",".join(list(set(found_materials)))
        print("Found bbmri material type: {0} for rd_connect input: {1}".format(found, rd_material_upper))
        return found
    else: 
        print("Set bbmri material type: [OTHER] for rd_connect input: {0}".format(rd_material_upper))
        return "OTHER"

def add_collections_info(eric_data, rd_data, sub_collections=True):
    """ adds disease information into bbmri_collection entity

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    rd_data : dict
        dictionary that holds rd_connect information (with EMX package/entity/attribute names)
    sub_collections : bool, optional
        generates parent collection (biobank/registry info) and subcollections (diseases) if True, else only
        collections are generated for diseases,
        by default True
    """

    # print(eric_data["eu_bbmri_eric_biobanks"])

    biobank_ids = eric_data["eu_bbmri_eric_biobanks"]['id']
    #orga_ids = biobank_id.str.split(pat=":")    #int(orga_id[-1])
    ids = []
    collection_class = ""

    count = 0
    for biobank_id in biobank_ids:
        m = rd_data['rd_diseases']['OrganizationID'] == int(biobank_id.split(':')[-1])
        basic_info_mask = rd_data['rd_basic_info']['OrganizationID'] == int(biobank_id.split(':')[-1])
        rows = rd_data['rd_diseases'][m]
        #a = pd.concat([a,list(biobank_id + ':collection:' +rows['name'])])
        if sub_collections:
            collection_class = "_pa"
            parent_id = str(biobank_id) + ':collection{0}'.format(collection_class)
            eric_data['eu_bbmri_eric_collections'].at[count,'id'] = parent_id
            collection_class = "_ch"
            count += 1

        rd_org_id = rd_data['rd_basic_info']['OrganizationID'] == int(biobank_id.split(':')[-1])
        rd_bb_mask = rd_data['rd_bb_core']['OrganizationID'] == int(biobank_id.split(':')[-1])
        rd_materials = rd_data["rd_bb_core"]["Additional_Biomaterial_available"][rd_bb_mask]

        if len(rd_materials) > 0 and not pd.isnull(rd_materials.values[0]):
            material_types = get_material_type(eric_data, rd_materials)

        org_type = rd_data["rd_basic_info"]["type"][rd_org_id].values[0]
        
        total_size = 0
        codes = []
        for enum,name in enumerate(rows['name'].values):
            ids.append(str(biobank_id) + ':collection:' +str(name))
            eric_data['eu_bbmri_eric_collections'].at[count,'id'] = str(biobank_id) + ':collection{0}:'.format(collection_class) + str(enum+1) + ":" + str(name)
            #split_id = str(str(biobank_id) + ':collection:' +str(r)).str.split(pat=":")
            eric_data['eu_bbmri_eric_collections'].at[count,'country']  = biobank_id.split(':')[2]
            eric_data['eu_bbmri_eric_collections'].at[count,'biobank']  = str(biobank_id)
            eric_data['eu_bbmri_eric_collections'].at[count,'name']  = str(name)

            mag = int(np.log10(np.max([1, rows.reset_index(drop=True).at[enum,'number']])))
            size = rows.reset_index(drop=True).at[enum,'number']
            total_size += size

            # eric_data['eu_bbmri_eric_collections'].at[count,'order_of_magnitude'] = mag
            eric_data['eu_bbmri_eric_collections'].at[count,'order_of_magnitude_donors'] = mag

            # eric_data['eu_bbmri_eric_collections'].at[count,'size'] = size
            eric_data['eu_bbmri_eric_collections'].at[count,'number_of_donors'] = size

            eric_data['eu_bbmri_eric_collections'].at[count,'type'] = 'RD'
            eric_data['eu_bbmri_eric_collections'].at[count,'contact_priority'] = 5
            eric_data['eu_bbmri_eric_collections'].at[count,'description'] = rows.reset_index(drop=True).at[enum,'synonym']
            eric_data['eu_bbmri_eric_collections'].at[count,'timestamp'] = pd.to_datetime(rd_data['rd_basic_info']['lastactivities'][basic_info_mask].values[0])

            code_list = check_disease_type(eric_data, rd_data, enum, name, rows, count)

            if code_list and len(code_list) > 0:
                codes.append(code_list)

            rd_org_id = rd_data['rd_basic_info']['OrganizationID'] == int(biobank_id.split(':')[-1])
            if "biobank" in rd_data["rd_basic_info"]["type"][rd_org_id].values[0]:
                data_cat = "BIOLOGICAL_SAMPLES,OTHER"
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = data_cat

                if pd.isnull(rd_materials.values[0]):
                    material_types = "NAV"
                    eric_data['eu_bbmri_eric_collections'].at[count,'materials'] = "NAV"

                else:
                    eric_data['eu_bbmri_eric_collections'].at[count,'materials'] = material_types


            elif "registry" in rd_data["rd_basic_info"]["type"][rd_org_id].values[0]:
                data_cat = "MEDICAL_RECORDS,OTHER"
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = data_cat
                material_types = "NAP"
                eric_data['eu_bbmri_eric_collections'].at[count,'materials'] = "NAP"
            else:
                data_cat = "OTHER"
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = data_cat

            if sub_collections:
                eric_data['eu_bbmri_eric_collections'].at[count,'parent_collection'] = parent_id

            count +=1

        if sub_collections:
            parent_mask = eric_data['eu_bbmri_eric_collections']["id"] == parent_id
            bb_name = rd_data['rd_basic_info'][basic_info_mask]["name"].values[0]
            total_mag = int(np.log10(np.max([1, total_size])))
            codes = [item for sublist in codes for item in sublist]

            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'country']  = biobank_id.split(':')[2]
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'biobank']  = str(biobank_id)
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'name']  = str(bb_name)
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'type'] = "RD"
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'contact_priority'] = 5
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'data_categories'] = data_cat
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'number_of_donors'] = total_size
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'order_of_magnitude_donors'] = total_mag
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'materials'] = material_types
            print(codes)
            eric_data['eu_bbmri_eric_collections'].at[parent_mask, 'diagnosis_available'] = ",".join(set(codes))

def get_country_code(eric_data, rd_data):
    """gets country code (ISO norm) eg.: AUSTRIA -> AUT ; UNITED STATS -> US etc
        missing / unknown: "ZZ"

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    rd_data : dict
        dictionary that holds rd_connect information (with EMX package/entity/attribute names)

    Returns
    -------
    data frame
        data frame countaining country codes of all countries. if no country specified: "ZZ"
    """
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
    """generates new biobank id using the following format: "rd_connect:ID:[COUNTRY_CODE]:[RD_CONNECT_ID]"
        eg.: "rd_connect:ID:US:11111"

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    bb_id : int
        biobank id from rd_connect

    Returns
    -------
    data frame
        data frame that holds biobank id for bbmri_eric in format: "rd_connect:ID:[COUNTRY_CODE]:[RD_CONNECT_ID]"
        eg.: "rd_connect:ID:US:11111"
    """

    id_list = ["rd_connect:ID:{0}:{1}".format(eric_data["eu_bbmri_eric_biobanks"]["country"].iloc[i],k) for i, k in enumerate(bb_id)]
    id_frame = pd.DataFrame(id_list)

    return id_frame

def add_organization_info(eric_data, rd_data):
    """adds mandatory biobank info: id, name, juridical_person, country, partner_charter_signed, contact_priority

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    rd_data : dict
        dictionary that holds rd_connect information (with EMX package/entity/attribute names)
    """

    # add MANDATORY information:
    bb_partner_cs = [False] # number of patients?
    contact_priority = [5] # positive integer

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


def add_geo_info(eric_data, rd_data, geo_file="biobank_location_info.xlsx", try_geolocator=False):
    """ adds longitude/latitude using provided file or geolocation service

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    rd_data : dict
        dictionary that holds rd_connect information (with EMX package/entity/attribute names)
    geo_file : str, optional
        filename of file with geo information, by default "biobank_location_info.xlsx"
    try_geolocator : bool, optional
        wether or not to use geolocator service, by default False
    """

    try:
        geo_info = pd.read_excel(geo_file, sheet_name=None)
        geo_df = geo_info["Sheet1"]
        for biobank in eric_data["eu_bbmri_eric_biobanks"]["id"]:
            longitude = geo_df[geo_df["id"] == biobank]["longitude"].values
            latitude = geo_df[geo_df["id"] == biobank]["latitude"].values

            eric_data["eu_bbmri_eric_biobanks"]["longitude"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = longitude
            eric_data["eu_bbmri_eric_biobanks"]["latitude"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = latitude

        return

    except FileNotFoundError:

        if not try_geolocator:
            print("[Error] \n")
            print("File [{0}] not found \n Use correct geo location file \n or set variable:  \"try_geolocator\" =True to use geolocation service".format(geo_file))
            print("Skipping Location info")
            return

        geolocator = geopy.geocoders.Nominatim(user_agent="get_loc_script")
        for biobank in eric_data["eu_bbmri_eric_biobanks"]["id"]:
            street = rd_data["rd_address"]["street1"][rd_data["rd_address"]["OrganizationID"] == int(biobank.split(":")[-1])].values

            if len(street) > 0:
                location = geolocator.geocode(street[0])

                if location:
                    longitude = location.longitude
                    latitude = location.latitude
                    eric_data["eu_bbmri_eric_biobanks"]["longitude"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = longitude
                    eric_data["eu_bbmri_eric_biobanks"]["latitude"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = latitude

def additional_organization_info(eric_data, rd_data):
    """ adds additional biobank info: description. acronym, person_id, organization-type ("registry" or "biobank")
        calls function "add_geo_info do add longitude/latitude

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    rd_data : dict
        dictionary that holds rd_connect information (with EMX package/entity/attribute names)
    """

    # add additional information:
    for biobank in eric_data["eu_bbmri_eric_biobanks"]["id"]:
        rd_id = int(biobank.split(":")[-1])
        description = rd_data["rd_core"]["Description"][rd_data["rd_core"]["OrganizationID"] == rd_id].values
        acronym = rd_data["rd_core"]["acronym"][rd_data["rd_core"]["OrganizationID"] == rd_id].values
        organization_type = rd_data["rd_basic_info"]["type"][rd_data["rd_basic_info"]["OrganizationID"] == rd_id].values
        eric_data["eu_bbmri_eric_biobanks"]["ressource_types"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = organization_type[0].upper()

        if biobank in eric_data["eu_bbmri_eric_persons"]["biobanks"].values:
            person_id = eric_data["eu_bbmri_eric_persons"]["id"][eric_data["eu_bbmri_eric_persons"]["biobanks"] == biobank].values
            eric_data["eu_bbmri_eric_biobanks"]["contact"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = person_id

        if pd.isnull(description) and biobank in rd_data["rd_bb_core"]["OrganizationID"].values:
            description = rd_data["rd_bb_core"]["Description"][rd_data["rd_bb_core"]["OrganizationID"] == rd_id].values

        if pd.isnull(acronym) and biobank in rd_data["rd_bb_core"]["OrganizationID"].values:
            acronym = rd_data["rd_core"]["acronym"][rd_data["rd_core"]["OrganizationID"] == rd_id].values
            

        eric_data["eu_bbmri_eric_biobanks"]["description"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = description
        eric_data["eu_bbmri_eric_biobanks"]["acronym"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = acronym


    add_geo_info(eric_data, rd_data)

def generate_contact_id(eric_data):
    """generates data frame that holds new IDs:
    format: rd_connect:contactID:[COUNTRY_CODE]_[COUNTER]

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)

    Returns
    -------
    data frame
        person ids
    """

    id_list = ["rd_connect:contactID:{0}_{1}".format(x.split(":")[2], k) for k, x in enumerate(eric_data["eu_bbmri_eric_persons"]["biobanks"])]
    id_frame = pd.DataFrame(id_list)

    return id_frame


def add_persons(eric_data, rd_data):
    """adds person information from rd_connect to data frame

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    rd_data : dict
        dictionary that holds rd_connect information (with EMX package/entity/attribute names)
    """
    eric_data["eu_bbmri_eric_persons"]["first_name"] = rd_data["rd_contacts"]["firstname"]
    eric_data["eu_bbmri_eric_persons"]["last_name"] = rd_data["rd_contacts"]["lastname"]
    eric_data["eu_bbmri_eric_persons"]["email"] = rd_data["rd_contacts"]["email"]
    eric_data["eu_bbmri_eric_persons"]["phone"] = rd_data["rd_contacts"]["phone"]
    
    bb_id = rd_data["rd_contacts"]["OrganizationID"]
    eric_data["eu_bbmri_eric_persons"]["biobanks"] = generate_bb_id(eric_data, bb_id) 
    eric_data["eu_bbmri_eric_persons"]["country"] = [org_id_long.split(":")[-2] for org_id_long in eric_data["eu_bbmri_eric_persons"]["biobanks"]]

    eric_data["eu_bbmri_eric_persons"]["id"] = generate_contact_id(eric_data)


def write_excel(eric_data, output_name):
    """writes dictionary of pandas dataframes to excel file

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    output_name : string
        file name for output file
    """
    with pd.ExcelWriter(output_name,engine='xlsxwriter') as writer:
        for sheet_name in eric_data.keys():
            df1 = eric_data[sheet_name]
            df1.to_excel(writer, sheet_name=sheet_name,index=False)

def rename_packages(eric_data, package_name):
    """rename package name (standart: bbmri_eric_eu)

    Parameters
    ----------
    eric_data : dict
        dictionary that holds bbmri_eric file (with EMX package/entity/attribute names)
    package_name : string
        new package name for output file. "bbmri_eric_eu" gets replaced by "package_name"

    Returns
    -------
    dict
        same dictionary as eric_data but with changed package name where needed
    """
    old_keys = list(eric_data.keys())
    new_keys = [key.replace("eu_bbmri_eric", package_name) for key in old_keys]
    new_dict = dict(zip(new_keys, eric_data.values()))
    new_dict["entities"] = new_dict["entities"].replace(["eu_bbmri_eric"], [package_name])
    new_dict["packages"]["name"] = package_name
    new_dict["packages"]["label"] = package_name
    new_dict["packages"]["description"] = package_name

    new_dict["attributes"]["entity"] = [val.replace("eu_bbmri_eric", package_name) for val in new_dict["attributes"]["entity"].values]
    new_dict["entities"]["extends"] = [val.replace("eu_bbmri_eric", package_name) if not pd.isnull(val) else "" for val in new_dict["entities"]["extends"].values]
    new_dict["attributes"]["refEntity"] = [val.replace("eu_bbmri_eric", package_name) if not pd.isnull(val) else "" for val in new_dict["attributes"]["refEntity"].values]

    return new_dict

if __name__ == "__main__":
    sub_collections = True

    eric_name = "empty_eric_duo.xlsx"
    rd_name = "rd_connect.xlsx"
    output_name = "rd_connect_eric_format_V1.xlsx"
    package_name = "rd_connect_v1"

    if sub_collections:
        output_name = "rd_connect_eric_format_V2.xlsx"
        package_name = "rd_connect_v2"

    rd_data = pd.read_excel(rd_name, sheet_name=None)
    eric_data = pd.read_excel(eric_name, sheet_name=None)

    add_organization_info(eric_data, rd_data)
    add_collections_info(eric_data, rd_data, sub_collections)
    add_persons(eric_data, rd_data)

    additional_organization_info(eric_data, rd_data)

    # change package name
    # eric_data = rename_packages(eric_data, package_name)
    write_excel(eric_data, output_name)
