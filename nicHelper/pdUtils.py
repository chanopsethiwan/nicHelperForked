# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/pdUtils.ipynb (unless otherwise specified).

__all__ = ['getDfHash', 'saveLocalCache', 'saveLocalHash', 'loadLocalCache', 'loadLocalHash', 'saveRemoteHash',
           'saveRemoteCache', 'loadRemoteCache', 'loadRemoteHash', 'PandasDataFrameAttribute', 'forceType']

# Cell
import pandas as pd
from hashlib import sha1
from .dictUtil import saveStringToFile, loadStringFromFile
from pynamodb.constants import BINARY
from pynamodb.attributes import Attribute, UnicodeAttribute
from pynamodb.models import Model
from beartype import beartype
from s3bz.s3bz import S3
import os, logging

# Cell
from io import BytesIO
from typing import Callable

@beartype
def getDfHash(df:pd.DataFrame,
              hashingAlgorithm: Callable = lambda x: sha1(x).hexdigest())->str:
  '''
    get a hash of a pandas dataframe\n
    this uses sha1 algorithm\n
    inputs:\n
      df: pd.DataFrame: a pandas dataframe\n
      hashingAlgoritm: callable: a hashing function which takes bytes input\n
    response:\n
      string hash\n
  '''
  f:BytesIO = BytesIO()
  df.to_feather(f)
  return hashingAlgorithm(f.read())


# Cell
def saveLocalCache( data:pd.DataFrame, path:str = '/tmp/cache',
                   saveHash:bool = True, force:bool = True):
  '''
    save cache of the dataframe to local location \n
    data:pd.DataFrame: dataframe to save \n
    path: str: path to save cache \n
    saveHash: bool: whether to save the hash digest
  '''
  ##check cache
  if not force:
    localHash = loadLocalHash(f'{path}.hash')
    dataHash = getDfHash(data)
    if dataHash == localHash :
      logging.debug('hash is the latest, skipping')
      return True
  ##save hash
  if saveHash:
    saveLocalHash(data, path=f'{path}.hash')
  # save cache
  logging.debug('saving cache')
  r =  data.to_feather(path)
  return r

def saveLocalHash( data:pd.DataFrame, path = '/tmp/cache.hash', force = False):
  '''
  save hash of the dataframe to local location \n
  data:pd.DataFrame: dataframe to save \n
  path: str: path to save hash
  '''
  dataHash = getDfHash(data)
  return saveStringToFile(dataHash,path)

def loadLocalCache( path = '/tmp/cache', throw = True):
  '''
  load cache of the dataframe from local location \n
  path: str: path to load cache
  '''
  if not os.path.exists(path):
    if throw:
      raise Exception('cache doesnt exist')
  return pd.read_feather(path)
def loadLocalHash( path = '/tmp/cache.hash'):
  '''
  load hash of the dataframe from local location \n
  path: str: path to load hash
  '''
  if not os.path.exists(path): raise Exception('hash doesnt exist')
  return loadStringFromFile(path)

# Cell
def saveRemoteHash(data:pd.DataFrame, key='', bucket='', **kwargs):
  '''
  save hash of the dataframe to S3 bucket \n
  data:pd.DataFrame: dataframe to save \n
  key: str: the name (key) of the dataframe to be saved in the S3 bucket \n
  bucket: str: the name of the bucket to store the dataframe
  '''
  hashKey = f'{key}-hash'
  hashString = getDfHash(data)
  dictToSave= {'hash': hashString }
  print(f'hashKey is {hashKey}')
  print('saving hash to s3')
  S3.save(key=hashKey,objectToSave=dictToSave, bucket=bucket, **kwargs )
  print(f'saved hash {hashString}')


def saveRemoteCache(data:pd.DataFrame, key = '',
                    bucket = '', localCachePath='/tmp/cache', localHashPath='/tmp/hash', **kwargs):
  '''
  save cache and hash of the dataframe to both local location and S3 bucket \n
  data:pd.DataFrame: dataframe to save \n
  key: str: the name (key) of the dataframe to be saved in the S3 bucket \n
  bucket: str: the name of the bucket to store the dataframe \n
  localCachePath: str:path to save cache locally \n
  localHashPath: str: path to save hash locally
  '''
  saveLocalCache(data=data, path = localCachePath)
  saveLocalHash(data=data, path = localHashPath)
  saveRemoteHash(data=data, key = key, bucket=bucket)
  S3.saveFile(key=key, path=localCachePath, bucket=bucket, **kwargs)

def loadRemoteCache(key='', bucket='', **kwargs):
  '''
  load cache of the dataframe from S3 bucket \n
  key: str: the name (key) of the dataframe to be loaded from the S3 bucket \n
  bucket: str: the name of the bucket to load the dataframe
  '''
  path = '/tmp/tmpPath'
  S3.loadFile(key,path=path ,bucket=bucket, **kwargs)
  df = pd.read_feather(path)
  return df

def loadRemoteHash(key='', bucket='', **kwargs):
  '''
  load hash of the dataframe from S3 bucket \n
  key: str: the name (key) of the dataframe to be loaded from the S3 bucket \n
  bucket: str: the name of the bucket to load the dataframe
  '''
  hashKey = f'{key}-hash'
  print(f'loading hashkey {hashKey}')
  loadedHash= S3.load(hashKey,bucket=bucket, **kwargs).get('hash')
  print(f'loaded hash is {loadedHash}')
  return loadedHash

# Cell
class PandasDataFrameAttribute(Attribute):
  '''
  pynamodb attributes for pandas dataframe
  '''
  attr_type = BINARY
  def serialize(self, value: pd.DataFrame)->bin:
    bio = BytesIO()
    value.to_feather(bio)
    data:bin = bio.getvalue()
    return data
  def deserialize(self, value: bin)->pd.DataFrame:
    bio = BytesIo(bin)
    df: pd.DataFrame = pd.read_feather(bio)
    return df

# Cell
# class PandasSeriesAttribute(Attribute):
#   attr_type = BINARY
#   def serialize(self, value: pd.Series)->bin:
#     bio = BytesIO()
#     df = s.to_frame()
#     value.to_feather(bio)
#     data:bin = bio.getvalue()
#     return data
#   def deserialize(self, value: bin)->pd.DataFrame:
#     bio = BytesIo(bin)
#     df: pd.DataFrame = pd.read_feather(bio)
#     return df

# Cell
from .schema import getTypes

# Cell
def forceType(url:str, df:pd.DataFrame, defaultType=str)->pd.DataFrame:
  '''
  force the data type in the dataframe to be the data type specified in the schema \n
  url: str: the url of the schema \n
  df: pd.DataFrame: a pandas dataframe \n
  defaultType: the default type of data if type of data is not specified, default = str
  '''
  typeDict = getTypes(url)
  typeList = {col:typeDict.get(col) for col in df.columns}
  print(typeList)
  df = df.astype(typeList)
  print(df.dtypes)
  return df