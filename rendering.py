import os
import yaml
from jinja2 import Environment, FileSystemLoader

config_data = yaml.load(open('./device_infos.yaml'))
env = Environment(loader = FileSystemLoader('./templates'),
    trim_blocks=True,
    lstrip_blocks=True
    template = env.get_template('template.j2')
    print(template.render(config_data))
)