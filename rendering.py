import yaml
from jinja2 import Environment, FileSystemLoader

config_data = yaml.load(open('./test.yaml'))

env = Environment(loader = FileSystemLoader('.'),
    trim_blocks=True,
    lstrip_blocks=True
)

template = env.get_template('test.j2')

print(template.render(config_data))