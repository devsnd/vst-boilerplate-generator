#!/usr/bin/env python3
#
# vst-boilerplate-generator
# Copyright (c) 2015 Tom Wallroth
#
# Sources on github:
#   http://github.com/devsnd/vst-boilerplate-generator/
#
# licensed under GNU GPL version 3 (or later)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

import sys
import os
from pathlib import Path
import json
import re
import random
from jinja2 import Template

usage = '''
    --create-effect-config EFFECT_NAME
    --create-effect EFFECT_NAME
'''

working_dir = Path(os.path.dirname(__file__))
config_dir = working_dir
template_dir = working_dir / 'templates'
vst_dir = working_dir / 'vsts'

config_path = working_dir / 'vst-boilerplate-generator-config.json'


class Config(dict):
    def __getattr__(self, attrname):
        return self[attrname]

    def __setattr__(self, attrname, attrval):
        self[attrname] = attrval

    @staticmethod
    def load(config_path):
        config = Config()
        with config_path.open('r') as fh:
            config.update(json.loads(fh.read()))
        return config

    def save(self, config_path):
        with config_path.open('w') as fh:
            fh.write(json.dumps(self, indent=4, sort_keys=True))


class Effect(object):
    def __init__(self, name, parent_path):
        self.parent_path = parent_path

        if not re.match('[\w\s]+', name):
            print('The name must be alphanumeric!')
            sys.exit(1)
        self.name = name
        # create default config
        self.config = Config()
        self.config.input_channels = 2
        self.config.output_channels = 2
        self.config.class_name = self.class_name()
        self.config.product_name = name
        self.config.program_name = name
        self.config.effect_name = name
        self.config.vendor_name = name
        self.config.vendor_version = 1000
        self.config.unique_id = random.randint(1000, 100000)
        self.config.parameters = [
            {
                'name': 'Gain',
                'label': 'dB',
                'variable_name': 'gain'
            }
        ]

    def dir_path(self):
        return self.parent_path / self.name

    def class_name(self):
        return self.name.title().replace('_', '')

    def canonical_name(self):
        return self.name.replace('_', '').lower()

    def config_file_path(self):
        return self.dir_path() / (self.class_name() + '-config.json')

    def sanitize_config(self):
        self.config.input_channels = min(2, self.config.input_channels)
        self.config.output_channels = min(2, self.config.output_channels)
        self.config.product_name = self.config.product_name.replace('"', '')
        self.config.program_name = self.config.program_name.replace('"', '')
        self.config.effect_name = self.config.effect_name.replace('"', '')
        self.config.vendor_name = self.config.vendor_name.replace('"', '')

    def save_config(self):
        self.sanitize_config()
        self.config.save(self.config_file_path())

    def load_config(self):
        self.config = Config.load(self.config_file_path())
        self.sanitize_config()


if not config_path.exists():
    print('''
============================================================
         VST Boilerplate Generator Configuration
============================================================

Make sure to download and extract the Steinberg VST SDK from 
http://www.steinberg.net/en/company/developers.html
if you havent already.

''')
    config = Config()
    config.sdk_abs_path = input('Please enter absolute path to the Steinberg VST SDK: ')
    config.save(config_path)
    print('Saved configuration to %s' % config_path)
else:
    config = Config.load(config_path)

valid_args = [
    '--create-effect-config',
    '--create-effect',
]

if sys.argv[1] not in valid_args:
    print(usage)
    sys.exit(1)

if sys.argv[1] == '--create-effect-config':
    effect = Effect(' '.join(sys.argv[2:]), vst_dir)
    effect_dir = effect.dir_path()
    if effect_dir.exists():
        print('The effect "%s" already exists!' % effect.name)
        sys.exit(1)
    effect_dir.mkdir()
    effect.save_config()

    vst_sdk_symlink = effect_dir / 'vst_sdk'
    vst_sdk_symlink.symlink_to(config.sdk_abs_path)

    print('A configuration file for you effect has been written to:\n')
    print('    %s\n' % effect.config_file_path())
    print('Edit the config to your will and then execute:\n')
    print('    %s --create-effect %s\n' % (sys.argv[0], effect.name))

if sys.argv[1] == '--create-effect':
    effect = Effect(' '.join(sys.argv[2:]), vst_dir)
    if not effect.dir_path().exists():
        print('The effect "%s" does not exist!' % effect.name)
        sys.exit(1)
    effect.load_config()

    templates = [
        'Makefile.jinja2',
        'linuxmain.cpp.jinja2',
        'effect.h.jinja2',
        'effect.cpp.jinja2',
    ]

    for template in templates:
        outfile_name = template.replace('.jinja2', '')
        template_path = template_dir / template
        outfile_path = effect.dir_path() / outfile_name

        with template_path.open('r') as infh:
            template = Template(infh.read())
            with outfile_path.open('w') as outfh:
                outfh.write(template.render(effect=effect))