import json
import os

def read_config(config_path, default_config):
    if not os.path.exists(config_path):
        print('No config file found, creating a new one...')
        with open(config_path, 'w') as config_file:
            json.dump(default_config, config_file)
        return default_config

    with open(config_path, 'r') as config_file:
        print('Loading config file...')
        config = json.load(config_file)

    # 确保所有必要的键都存在
    if 'column_widths' not in config:
        print('column_widths not found in config, creating a new one...')
        config['column_widths'] = {}

    if 'splitter_ratio' not in config:
        print('splitter_ratio not found in config, creating a new one...')
        config['splitter_ratio'] = [0.15776699029126215, 0.8422330097087378]
    
    if 'window_size' not in config:
        print('window_size not found in config, creating a new one...')
        config['window_size'] = [800, 600]

    return config
