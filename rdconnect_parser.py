import json


with open("rdconnectfinder.json") as f:
    file = dict(json.load(f))

print(list(file.keys())[0])
print("Type: ", type(file[list(file.keys())[0]]))
print("list[0]: ", type(file[list(file.keys())[0]][0]))
print("Entries: ", len(file[list(file.keys())[0]]))
print(file[list(file.keys())[0]][0].keys())
print("\n", file[list(file.keys())[0]][0]["address"])
print("\n", file[list(file.keys())[0]][0]["diseases"])
print("\n", file[list(file.keys())[0]][0]["date of inclusion"])
print("\n", file[list(file.keys())[0]][0]["OrganizationID"])
print("\n", file[list(file.keys())[0]][0]["type"])
print("\n", file[list(file.keys())[0]][0]["url"])