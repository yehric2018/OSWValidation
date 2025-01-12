from jsonschema import Draft7Validator
from config import DefaultConfigs
import json
import os
from os import path
import sys
import ntpath

def minItems_error(errors,index):
    if len(errors.schema_path)==8 and errors.schema_path[7]=='minItems' and errors.schema_path[4]=='geometry':
        return str(errors.instance) + ". LineString(Way) Geometry should contain atleast 2 coordinates"
    else:
        return errors.message + " max for " + str(errors.schema_path[index - 1])

def maxItems_error(errors,index):
    if len(errors.schema_path)==8 and errors.schema_path[7]=='maxItems' and errors.schema_path[4]=='geometry':
        return "Point Geometry should contain only 1 coordinate"
    else:
        return errors.message + " min for " + str(errors.schema_path[index - 1])

def type_item_error(errors):
    if len(errors.schema_path)==10 and errors.schema_path[6]=='coordinates' and errors.schema_path[4]=='geometry' and errors.schema_path[9]=="type":
        return str(errors.instance) + " - please remove the extra points. Point Geometry should contain only 1 coordinate"

def required_errors(errors,index):
	if str(errors.schema_path[index-2]) == "dependencies":
		return errors.message + " for " + str(errors.schema_path[index-1])
	elif str(errors.schema_path[index-2]) == "allOf":
		return errors.message + " for " + str(errors.schema_path[index-3])


def error_capture(key,errors,index):
    errordict = {
        "required": required_errors(errors,index),
        "maxItems": maxItems_error(errors,index),
        "minItems": minItems_error(errors,index),
        "maximum":  errors.message + " allowed for property " +  str( errors.schema_path[index-1]),
        "minimum": errors.message + " allowed for property " + str( errors.schema_path[index-1]),
        "additionalProperties": (errors.message.split('(')[-1]).split(' ')[0] + " is not a valid OSW tag",
        "const": "'" + str(errors.schema_path[index-1]) + "':" + errors.message,
        "enum": errors.message + " that are allowed for " + str( errors.schema_path[index-1]),
        "anyOf": errors.message.split('}')[0] + "} missing required supporting tags",
        #"additionalItems": str(errors.instance) + " - Only one of the coordinate or point should be there",
        #"type": type_item_error(errors)
    }
    return errordict.get(key)
    #return errordict.get(key, errors.message + " MISSED CAPTURING THIS " + errors.schema_path[index])


def validate_json_structure_with_schema(geojson, schema):
    validator = Draft7Validator(schema)
    errors = validator.iter_errors(geojson)

    invalid_ids = dict()  # A dictionary to hold IDs of invalid nodes and error messages
    for error in errors:
        if not error.path:
            continue
        if error.path[1] not in invalid_ids.keys():
            invalid_ids.update({error.path[1]: list()})
        index = len(error.schema_path) - 1
        print(error.message)
        error_message = error_capture(error.schema_path[index], error, index)
		
        if error_message:
            invalid_ids[error.path[1]].append(error_message)

    return invalid_ids

def validate_json_structure(geojson):
    schema_filename = './OSWValidation/Json Schema/Ways_schema.json'

    try:
        wd = sys._MEIPASS
    except AttributeError:
        wd = os.getcwd()
    file_path = path.join(wd, schema_filename)

    with open(os.path.abspath(file_path), 'r') as fp:
        schema = json.load(fp)

    return validate_json_structure_with_schema(geojson, schema)
