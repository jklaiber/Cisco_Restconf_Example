import logging
from typing import List
import requests
import yaml
import restconf_helpers
import rendering

requests.packages.urllib3.disable_warnings()
logger = logging.getLogger('restconf.example')
MAX_RETRIES = 3;
ERROR_CODE_409 = 409

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

def patch_configuration(host: dict, retries = 0) -> int:
    rendering_data = rendering.RenderJinjaTemplate().rendering(host)
    rendered_xml_data = rendering.XmlParser().parseXml(rendering_data)

    response_code = restconf_helpers.RestconfRequestHelper().patch(
        url=f'https://{host["connection_address"]}/restconf/data/Cisco-IOS-XE-native:native/',
        username=host['username'],
        password=host['password'],
        data=rendered_xml_data)
    if(ERROR_CODE_409 == response_code and retries <= MAX_RETRIES):
        patch_configuration(host, retries+1)
    elif(retries > MAX_RETRIES):
        logger.error('409 Conflict status-line. The error-tag value object already exists is returned if used for other methods or resource types.\n 409 Client Error: Conflict')
    return response_code

def main():
    devices = load_devices() 
    for device in devices:
        logger.info
        logger.info(f'Getting information for device {device["hostname"]}')
        response_code = patch_configuration(device)
        if( int(response_code/100) == 2): #Because successfull Response Messages are 200, 201 and 204 more info: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/166/b_166_programmability_cg/restconf_prog_int.html
            logger.info(f'SUCCESS: Ended device {device["hostname"]} with response code {response_code} \n')
        else:
            logger.warning(f'ERROR: Ended device {device["hostname"]} with response code {response_code} \n')
    

if __name__ == '__main__':
    init_logger()
    main()


