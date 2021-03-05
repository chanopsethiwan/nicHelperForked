# AUTOGENERATED! DO NOT EDIT! File to edit: schema.ipynb (unless otherwise specified).

__all__ = ['validateUrl', 'getTypes', 'typeMapJsonSchema', 'typeMap']

# Cell
import jsonschema, requests, yaml
from types import SimpleNamespace

# Cell
def validateUrl(url,input_, format_ = 'json'):
  if format_ == 'yaml':
    schemaYaml = requests.get(url).text
    schema = yaml.load(schemaYaml, Loader=yaml.FullLoader)
  elif format_ == 'json':
    schema = requests.get(url).json()
  else:
    print('invalid schema format, using json')
    schema = requests.get(url).json()
  res = jsonschema.validate(input_,schema)
  return SimpleNamespace(**input_)

# Cell
typeMap = {'string': str, 'number': float, 'integer': int, 'object': dict, 'array': list, 'boolean': bool, 'null': None}
def getTypes(schemaUrl:str, typeMap:dict=typeMap)->dict:
  '''get python types from json schema'''
  r = requests.get(schemaUrl)
  s = yaml.load(r.text, Loader=yaml.FullLoader)
  properties = s['properties']
  dtypes = {k: typeMap.get(v['type']) for k,v in properties.items()}
  return dtypes
def typeMapJsonSchema(url:str, input_:dict = {}, typeMap:dict = typeMap, defaultType=str):
  '''
  try to map the datatype into the one specified in url of json schema.
  if type is not found, the defaultType is used
  '''
  typesDict = getTypes(url, typeMap=typeMap) # get dtype from schema url
  print(f'typesDict is: {typesDict}')
  convertedInput = {k: (typesDict.get(k) or defaultType)(v) for k,v in input_.items()}
  return convertedInput

