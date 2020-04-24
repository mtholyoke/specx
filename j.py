#!/usr/bin/env python3

import yaml

config = {
    'host': '0.0.0.0',
    'port': '51515',
    'secret_key': 'Nautilus',
    'debug': False,
}
try:
    config_file = open('config.yml')
    config_yaml = yaml.safe_load(config_file)
    for key in config.keys():
        if key in config_yaml.keys():
            config[key] = config_yaml[key]
    config_file.close()
except IOError:
    print("Can’t read config.yml; using defaults")

print(config)
