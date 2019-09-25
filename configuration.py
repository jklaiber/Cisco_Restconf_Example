import logging
from typing import List
import requests
import yaml
import restconf_helpers
import rendering

requests.packages.urllib3.disable_warnings()
logger = logging.getLogger('restconf.example')

def init_logger():
    _logger = logging.getLogger('restconf')
    _logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    _logger.addHandler(ch)

def load_devices() -> List[dict]:
    with open('device_infos.yaml', 'r') as host_file:
        hosts = yaml.load(host_file.read(), Loader=yaml.FullLoader)
        return hosts

def get_hostname(host: dict) -> str:
    response = restconf_helpers.RestconfRequestHelper().get(
        url=f'https://{host["connection_address"]}/restconf/data/Cisco-IOS-XE-native:native/hostname/',
        username=host['username'],
        password=host['password'])
    return response

def patch_configuration(host: dict) -> str:
    rendering_data = rendering.RenderJinjaTemplate().rendering(host)
    print(rendering_data)
    rendered_xml_data = rendering.XmlParser().parseXml(rendering_data)

    print(rendered_xml_data)
    response = restconf_helpers.RestconfRequestHelper().patch(
        url=f'https://{host["connection_address"]}/restconf/data/Cisco-IOS-XE-native:native/',
        username=host['username'],
        password=host['password'],
        data=rendered_xml_data)
    return response

def main():
    devices = load_devices() 
    for device in devices:
        logger.info
        logger.info(f'Device Information: {device}')
        logger.info(f'Getting information for device {device["hostname"]}')
        response = patch_configuration(device)
        print(response)

if __name__ == '__main__':
    init_logger()
    main()


