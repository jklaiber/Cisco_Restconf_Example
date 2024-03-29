import yaml
from jinja2 import Environment, FileSystemLoader
import xml.dom.minidom as dom

class RenderJinjaTemplate:

    def rendering(self, config_data: dict) -> str:        
        env = Environment(loader = FileSystemLoader('./template'),
            trim_blocks=True,
            lstrip_blocks=True
        )
        template = env.get_template('default_template.xml')
        rendereddata = template.render(config_data)
        return rendereddata
    
class XmlParser:

    def parseXml(self, input_xml: str) -> str:
        _dom = dom.parseString(input_xml)
        output_xml = ''.join([line.strip() for line in _dom.toxml().splitlines()])
        _dom.unlink()
        return output_xml