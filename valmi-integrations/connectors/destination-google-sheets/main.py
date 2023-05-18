#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_google_sheets import DestinationGoogleSheets

if __name__ == "__main__":
    DestinationGoogleSheets().run(sys.argv[1:])
'''
mapping = [
    {"stream":"users", "sink":"test_users"},
    {"stream":"simpletest2", "sink":"sk_simpletest2"},

    {"stream":"simpletest", "sink":"sk_simpletest"},
    {"stream":"simpletest2", "sink":"tk_simpletest2"}   ,
        {"stream":"users", "sink":"sk_users"}

]
src_fields = list(map(lambda map_obj: (map_obj["stream"], map_obj,), mapping))
dst_fields = list(map(lambda map_obj: (map_obj["sink"], map_obj,), mapping))

headers = []
for key in sorted(list(["simpletest2","simpletest"])):
    filtered_src_fields= list(filter(lambda x: x[0] == key, src_fields))
    if len(filtered_src_fields) > 0:
        for src_field_obj in filtered_src_fields:
            headers.append(src_field_obj[1]["sink"])
    else:
        headers.append(key)

print( {
            "headers": headers,
            "stream_properties": sorted(list(["simpletest2","simpletest"])),
            "is_set": False,
        }
)


'''