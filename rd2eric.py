import json
import xlsxwriter
import pandas as pd
import re
import numpy as np
import geopy


def add_code_to_types(eric_data, code, code_id, name):

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

    found_av = 0
    code_nan = 0
    found = 0

    icd_code = rows.reset_index(drop=True).at[enum,'icd10']
    orpha_code = rows.reset_index(drop=True).at[enum,'orphacode']
    code_frame = eric_data['eu_bbmri_eric_disease_types']['code'].values

    if pd.isnull(icd_code) and pd.isnull(orpha_code):
        code_nan += 1
        return found_av, code_nan, found

    if not pd.isnull(orpha_code):
        orpha_codes = ["ORPHA:" + orph for orph in re.findall(r'\d+', orpha_code)]
        # print("before list comp: \n", orpha_code)
        # print("\n after: \n ", orpha_codes)
        code_list = []
        for code in orpha_codes:
            if code in code_frame:
                code_list.append(str(code))
            else:
                code_id = code
                add_code_to_types(eric_data, code, code_id, name)

        found_av += 1

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
            if code in code_frame:
                code_list.append("urn:miriam:icd:"+str(code))

            else:
                if rex.match(code):
                    code_id = "urn:miriam:icd:"+str(code)
                    add_code_to_types(eric_data, code, code_id, name)

        found_av += 1

        # make sure that codes occur only once
        code_list = sorted(list(set(code_list)))
        eric_data['eu_bbmri_eric_collections'].at[count,'diagnosis_available'] = ",".join(code_list)

    return found_av, code_nan, found

def add_collections_info(eric_data, rd_data):
    bb_type = ["RD"]
    bb_data_cat = "MEDICAL RECORDS" # OR OTHER?

    print(eric_data["eu_bbmri_eric_biobanks"])

    biobank_ids = eric_data["eu_bbmri_eric_biobanks"]['id']
    #orga_ids = biobank_id.str.split(pat=":")    #int(orga_id[-1])
    ids = [] 

    count = 0
    code_found = 0
    code_nan = 0
    code_found_av = 0
    for biobank_id in biobank_ids:
        m = rd_data['rd_diseases']['OrganizationID'] == int(biobank_id.split(':')[-1])
        basic_info_mask = rd_data['rd_basic_info']['OrganizationID'] == int(biobank_id.split(':')[-1])
        rows = rd_data['rd_diseases'][m]
        #a = pd.concat([a,list(biobank_id + ':collection:' +rows['name'])])
        for enum,name in enumerate(rows['name'].values):
            ids.append(str(biobank_id) + ':collection:' +str(name))
            eric_data['eu_bbmri_eric_collections'].at[count,'id'] = str(biobank_id) + ':collection:' + str(enum+1) + ":" + str(name)
            #split_id = str(str(biobank_id) + ':collection:' +str(r)).str.split(pat=":")
            eric_data['eu_bbmri_eric_collections'].at[count,'country']  = biobank_id.split(':')[2]
            eric_data['eu_bbmri_eric_collections'].at[count,'biobank']  = str(biobank_id)
            eric_data['eu_bbmri_eric_collections'].at[count,'name']  = str(name)

            eric_data['eu_bbmri_eric_collections'].at[count,'order_of_magnitude'] = int(np.log10(np.max([1, rows.reset_index(drop=True).at[enum,'number']])))
            eric_data['eu_bbmri_eric_collections'].at[count,'order_of_magnitude_donors'] = int(np.log10(np.max([1, rows.reset_index(drop=True).at[enum,'number']])))

            eric_data['eu_bbmri_eric_collections'].at[count,'size'] = rows.reset_index(drop=True).at[enum,'number']
            eric_data['eu_bbmri_eric_collections'].at[count,'number_of_donors'] = rows.reset_index(drop=True).at[enum,'number']

            eric_data['eu_bbmri_eric_collections'].at[count,'type'] = 'RD'
            eric_data['eu_bbmri_eric_collections'].at[count,'contact_priority'] = 5
            eric_data['eu_bbmri_eric_collections'].at[count,'description'] = rows.reset_index(drop=True).at[enum,'synonym']
            eric_data['eu_bbmri_eric_collections'].at[count,'timestamp'] = pd.to_datetime(rd_data['rd_basic_info']['lastactivities'][basic_info_mask].values[0])

            found_av, nan, found = check_disease_type(eric_data, rd_data, enum, name, rows, count)
            code_found_av += found_av
            code_nan += nan
            code_found += found

            rd_org_id = rd_data['rd_basic_info']['OrganizationID'] == int(biobank_id.split(':')[-1])
            if "biobank" in rd_data["rd_basic_info"]["type"][rd_org_id].values[0]:
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = "BIOLOGICAL_SAMPLES,OTHER"

            elif "registry" in rd_data["rd_basic_info"]["type"][rd_org_id].values[0]:
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = "MEDICAL_RECORDS,OTHER"
            else:
                eric_data['eu_bbmri_eric_collections'].at[count,'data_categories'] = "OTHER"

            count +=1

    print("Total diseases: ", count)
    print("Found in disease types: ", code_found)
    print("Found/Av: ", 100*code_found_av/count)
    print("Found: ", 100*code_found/count)
    print("NaN: ", 100* code_nan/count)

    # for k, id_ in enumerate(ids):
    #     eric_data['eu_bbmri_eric_collections'].at[k,'id']  = id_

    # splits_ids = eric_data['eu_bbmri_eric_collections']['id'].str.split(pat=":")     

    # for k, split_id in enumerate(splits_ids):
    #     eric_data['eu_bbmri_eric_collections'].at[k,'country']  = split_id[2]
    #     eric_data['eu_bbmri_eric_collections'].at[k,'biobank']  = split_id[0] +':'+split_id[1] +':'+split_id[2] +':'+split_id[3]
    #     eric_data['eu_bbmri_eric_collections'].at[k,'name']  = split_id[5]



    #fill eric_data['eu_bbmri_eric_collections']
    #take oranis id info   eric_data['eu_bbmri_eric_biobanks'], look id up in   rd_data['rd_diseases']  = create id and have all infos together

    #rd_data['rd_diseases']['OrganizationID'] == '11193'

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

def generate_bb_id(eric_data, bb_id):

    id_list = ["rd_connect:ID:{0}:{1}".format(eric_data["eu_bbmri_eric_biobanks"]["country"].iloc[i],k) for i, k in enumerate(bb_id)]
    id_frame = pd.DataFrame(id_list)

    return id_frame

def add_biobank_info(eric_data, rd_data):

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


def add_geo_info(eric_data, rd_data):

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

def additional_biobank_info(eric_data, rd_data):

    # add additional information:
    for biobank in eric_data["eu_bbmri_eric_biobanks"]["id"]:
        rd_id = int(biobank.split(":")[-1])
        description = rd_data["rd_core"]["Description"][rd_data["rd_core"]["OrganizationID"] == rd_id].values
        acronym = rd_data["rd_core"]["acronym"][rd_data["rd_core"]["OrganizationID"] == rd_id].values

        if biobank in eric_data["eu_bbmri_eric_persons"]["biobanks"].values:
            person_id = eric_data["eu_bbmri_eric_persons"]["id"][eric_data["eu_bbmri_eric_persons"]["biobanks"] == biobank].values
            eric_data["eu_bbmri_eric_biobanks"]["contact"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = person_id

        if pd.isnull(description) and biobank in rd_data["rd_bb_core"]["OrganizationID"].values:
            description = rd_data["rd_bb_core"]["Description"][rd_data["rd_bb_core"]["OrganizationID"] == rd_id].values

        if pd.isnull(acronym) and biobank in rd_data["rd_bb_core"]["OrganizationID"].values:
            acronym = rd_data["rd_core"]["acronym"][rd_data["rd_core"]["OrganizationID"] == rd_id].values


        eric_data["eu_bbmri_eric_biobanks"]["description"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = description
        eric_data["eu_bbmri_eric_biobanks"]["acronym"].at[eric_data["eu_bbmri_eric_biobanks"]["id"] == biobank] = acronym


    # add_geo_info(eric_data, rd_data)

def generate_contact_id(eric_data):

    id_list = ["rd_connect:contactID:{0}_{1}".format(x.split(":")[2], k) for k, x in enumerate(eric_data["eu_bbmri_eric_persons"]["biobanks"])]
    id_frame = pd.DataFrame(id_list)

    return id_frame


def add_persons(eric_data, rd_data):
    eric_data["eu_bbmri_eric_persons"]["first_name"] = rd_data["rd_contacts"]["firstname"]
    eric_data["eu_bbmri_eric_persons"]["last_name"] = rd_data["rd_contacts"]["lastname"]
    eric_data["eu_bbmri_eric_persons"]["email"] = rd_data["rd_contacts"]["email"]
    eric_data["eu_bbmri_eric_persons"]["phone"] = rd_data["rd_contacts"]["phone"]
    
    bb_id = rd_data["rd_contacts"]["OrganizationID"]
    eric_data["eu_bbmri_eric_persons"]["biobanks"] = generate_bb_id(eric_data, bb_id) 
    eric_data["eu_bbmri_eric_persons"]["country"] = [org_id_long.split(":")[-2] for org_id_long in eric_data["eu_bbmri_eric_persons"]["biobanks"]]

    eric_data["eu_bbmri_eric_persons"]["id"] = generate_contact_id(eric_data)


def write_excel(eric_data, eric_name, output_name):
    
    with pd.ExcelWriter(output_name,engine='xlsxwriter') as writer:
        for sheet_name in eric_data.keys():
            df1 = eric_data[sheet_name]
            df1.to_excel(writer, sheet_name=sheet_name,index=False)


if __name__ == "__main__":
    eric_name = "rd2eric.xlsx"
    rd_name = "rd_connect.xlsx"
    output_name = "rd_connect_eric_format.xlsx"

    rd_data = pd.read_excel(rd_name, sheet_name=None)
    eric_data = pd.read_excel(eric_name, sheet_name=None)

    add_biobank_info(eric_data, rd_data)
    add_collections_info(eric_data, rd_data)
    add_persons(eric_data, rd_data)

    additional_biobank_info(eric_data, rd_data)

    write_excel(eric_data, eric_name, output_name)
