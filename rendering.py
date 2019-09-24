import yaml
from jinja2 import Environment, FileSystemLoader



class RenderJinjaTemplate:

    def rendering(self, config_data: dict):
        # config_data = yaml.load(open('./test.yaml'))
        
        env = Environment(loader = FileSystemLoader('./template'),
            trim_blocks=True,
            lstrip_blocks=True
        )

        template = env.get_template('default_template.xml')

        rendereddata = template.render(config_data)
        return rendereddata