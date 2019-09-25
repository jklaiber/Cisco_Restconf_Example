# CldInf_Lab2
## What it makes
The application should automatically deploy things like interfaces
ospf routing and bgp routing.
Currently there is only Cisco Native support.

## Requirements
```bash
$ TODO venv configuration
$ source activate /bin/activate
$ pip3 install -r requirements.txt
```

## Work with it
1. Open the device_infos.yaml file
2. Edit the configuration to your needs
3. You can add additional bgp neighbors or ospf areas and also interfaces
4. When you need a additional router then you can also do that (please consider the yaml sintax)

**Run**: `python3 configuration.py`

## Code Explanation
### rendering.py
Class for render the jinja2 template and the xml. 
We have to render the xml because cisco devices can only handle a single one line string and unfortunately no formatted xml.

**rendering()**  
Rendering method for jinja2 which will make a own environment. In the environment we can open the template folder and render the template with the config data we become from the configuration.py
```python
def rendering(self, config_data: dict):        
    env = Environment(loader = FileSystemLoader('./template'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template('default_template.xml')
    rendereddata = template.render(config_data)
    return rendereddata
```
**parseXml()**  
This method is used to parse the xml from a formated file into a single line.
```python
def parseXml(self, input_xml: dict):
    _dom = dom.parseString(input_xml)
    output_xml = ''.join([line.strip() for line in _dom.toxml().splitlines()])
    _dom.unlink()
    return output_xml
```
### restconf_helpers.py
Class for getting information from the device and patch configuration onto the device.  
  
**patch()**  
TODO
```python
def patch(self, url: str, username: str, password: str,
    data: str,
    restconf_format: Optional[RestconfFormat] = RestconfFormat.XML,
    headers: Optional[Dict[str, str]] = None,
    **kwargs: Dict[Any, Any]) -> str:
            
    """Executes a patch to the specified url updates the config of device.
    Raises an exception if the request fail        
    Parameters:
        url: url which should be requested
        username: the username for the authentication
        password: the password for the authentication
        restconf_format: which restconf headers should be set. (default RestconfFormat.XML)
        headers: which additional headers should be set (default None)
        kwargs: additional parameters for the reques        
    Returns:
        str: The text of the response
    """
    logger.debug(f'PATCH request to {url}')
    request_headers = self.get_headers(restconf_format, headers)
    response = requests.request(method='PATCH',
                                auth=(username, password),
                                headers=request_headers,
                                data=data,
                                url=url,
                                verify=False,
                                **kwargs)
    logger.debug(f'Got response from {url} with code {response.status_code} and content \n {response.text}')
    response.raise_for_status()
    return response.text
```
### configuration.py

**load_devices()**  
TODO
```python
def load_devices() -> List[dict]:
    with open('device_infos.yaml', 'r') as host_file:
        hosts = yaml.load(host_file.read(), Loader=yaml.FullLoader)
        return hosts
```
**get_hostname()**  
TODO
```python
def get_hostname(host: dict) -> str:
    response = restconf_helpers.RestconfRequestHelper().get(
        url=f'https://{host["connection_address"]}/restconf/data/Cisco-IOS-XE-native:native/hostname/',
        username=host['username'],
        password=host['password'])
    return response

```
**patch_configuration()**  
TODO
```python
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
```



# Contributors
- Julian Klaiber (<julian.klaiber@hsr.ch>)
- Severin Dellsperger (<severin.dellsperger@hsr.ch>)