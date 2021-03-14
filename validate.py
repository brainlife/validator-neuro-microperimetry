#!/usr/bin/env python3

import os
import json
import pandas

with open('config.json', encoding='utf8') as config_json:
    config = json.load(config_json)

errors = []
warnings = []
meta = {}

path=config["microperimetry"]

df = pandas.read_table(path, delim_whitespace=True)

if not os.path.exists("output"):
    os.mkdir("output")

if not os.path.exists("secondary"):
    os.mkdir("secondary")

if len(df.columns) != 4:
    errors.append("there should be exactly 4 columns")

expected_columns = ['ID', 'x_deg', 'y_deg', 'Threshold']
i = 0
while i < len(expected_columns):
    if df.columns[i] != expected_columns[i]:
        errors.append("column %d header should be %s" %((i+1), expected_columns[i]))
    i+=1

df.to_csv("output/microperimetry.tsv", index=False, sep='\t')

with open("product.json", "w") as fp:
    json.dump({"errors": errors, "warnings": warnings, "meta": meta}, fp)

print("warnings--")
print(warnings)
print("errors--")
print(errors)

print("done");
