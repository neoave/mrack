# Copyright 2020 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import base64
import datetime
import json

from .errors import ConfigError


def get_config_value(config_dict, key, default=None):
    '''
    Usable for dictionaries which can also contain attribute 'default'

    Order of preference:
    * attribute value
    * value of 'default' attribute
    * value of provided default param
    '''
    val = config_dict.get(key)
    if val is None:
        val = config_dict.get('default', default)
    return val


def validate_dict_attrs(dct, attr_list, dct_name):
    '''
    Validate that dictionary contains all atributes from provided attribute
    list.
    '''
    missing = [a for a in attr_list if a not in dct]
    if missing:
        error = f'''
        '{dct_name} definition:'
        {dct}
        'Is missing required attributes: {missing}'
        '''
        raise ConfigError(error)


def json_convertor(obj):
    '''
    To be used for json.dumps as value for default= so that given object
    is serializable
    '''

    if "Binary" in str(obj.__class__):
        return base64.b64encode(obj.data).decode("utf-8")

    if "DateTime" in str(obj.__class__):
        date = datetime.datetime.strptime(str(obj), '%Y%m%dT%H:%M:%S')
        return date.isoformat() + "Z"

    if "Decimal" in str(obj.__class__):
        return str(obj)


def print_obj(obj):
    '''
    Print object as JSON
    '''
    print(json.dumps(obj, default=json_convertor, sort_keys=True, indent=4))
