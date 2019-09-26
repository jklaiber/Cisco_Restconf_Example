# CldInf_Lab2
## What the tool accomplish
The application automatically configures features on Cisco devices.
Following configuration changes are supported:
- Hostname
- Interface
- OSPF
- BGP

Currently there is only Cisco Native support.
The features are tested on Cisco CSR1000v with IOS XE 16.06.01.

## Requirements
```bash
$ python3 –m venv path/to/desired/dir
$ source activate /bin/activate
$ pip3 install -r requirements.txt
```

## Work with it
1. Open the `device_infos.yaml` file
2. Edit the configuration to meet your needs
3. You can add additional bgp neighbors or ospf areas and also interfaces
4. When you need an additional router then you can also do that (please consider the yaml syntax)
5. Run & enjoy it.

You can find an example of `device_infos.yaml` at the end of this document.

**Run**: `python3 configuration.py`

## Code Explanation

### configuration.py

**main**
Starting Point:
The main function loads the devices and executes a HTTP PATCH request for each device. 
```python
def main():
    devices = load_devices() 
    for device in devices:
        logger.info
        logger.info(f'Device Information: {device}')
        logger.info(f'Getting information for device {device["hostname"]}')
        response = patch_configuration(device)
        logger.info(f'Response answer: {response}')
```

**load_devices()**  
Read the input of the configuration file ```device_infos.yaml``` and return a list of dicts including the config information. 
```python
def load_devices() -> List[dict]:
    with open('device_infos.yaml', 'r') as host_file:
        hosts = yaml.load(host_file.read(), Loader=yaml.FullLoader)
        return hosts
```
**get_hostname()**  
Request the hostname of a given host with a HTTP GET request and return it.
```python
def get_hostname(host: dict) -> str:
    response = restconf_helpers.RestconfRequestHelper().get(
        url=f'https://{host["connection_address"]}/restconf/data/Cisco-IOS-XE-native:native/hostname/',
        username=host['username'],
        password=host['password'])
    return response

```
**patch_configuration()**  
- Rendering the given host dict (which includes the configuration information) into a correct XML format.
- Render XML into one single lined string (because Cisco the devices only support this format)
- Configure the device with sending the information via HTTP PATCH request to the REST API.
- Calling the REST API the HTTP respone will be returned.
```python
def patch_configuration(host: dict) -> str:
    rendering_data = rendering.RenderJinjaTemplate().rendering(host)
    rendered_xml_data = rendering.XmlParser().parseXml(rendering_data)

    response = restconf_helpers.RestconfRequestHelper().patch(
        url=f'https://{host["connection_address"]}/restconf/data/Cisco-IOS-XE-native:native/',
        username=host['username'],
        password=host['password'],
        data=rendered_xml_data)
    return response
```

### rendering.py
Class for rendering the given jinja2 template and the XML. 
Rendering XML is essential because Cisco devices only
support one single line string and no correct formatted XML.


**rendering()**  
Rendering function for jinja2 which creates an own environment. In the environment we can open the template folder and render the template with the config data we got in the config_data argument.
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
Parse a correct formatted XML file into a single line.
```python
def parseXml(self, input_xml: dict):
    _dom = dom.parseString(input_xml)
    output_xml = ''.join([line.strip() for line in _dom.toxml().splitlines()])
    _dom.unlink()
    return output_xml
```
### restconf_helpers.py
Class for getting information from the device and patch configuration onto the device.  

**get()**
Executes a get request to the specified url and adds RESTCONF specific headers.
Raises an exception if the request fails.
Parameters:
            url: url which should be requested
            username: the username for the authentication
            password: the password for the authentication
            restconf_format: which restconf headers should be set. (default RestconfFormat.XML)
            headers: which additional headers should be set (default None)
            kwargs: additional parameters for the request

        Returns:
            str: The text of the response

```python
def get(self, url: str, username: str, password: str,
            restconf_format: Optional[RestconfFormat] = RestconfFormat.XML,
            headers: Optional[Dict[str, str]] = None,
            **kwargs: Dict[Any, Any]) -> str:

        logger.debug(f'GET request to {url}')
        request_headers = self.get_headers(restconf_format, headers)
        response = requests.request(method='GET', auth=(username, password),
                                    headers=request_headers,
                                    url=url,
                                    verify=False,
                                    **kwargs)
        logger.debug(f'Got response from {url} with code {response.status_code} and content \n {response.text}')
        response.raise_for_status()
        return response.text
```
  
**patch()**  
 Executes a patch to the specified url and updates the configuration of the device.
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

```python
def patch(self, url: str, username: str, password: str,
    data: str,
    restconf_format: Optional[RestconfFormat] = RestconfFormat.XML,
    headers: Optional[Dict[str, str]] = None,
    **kwargs: Dict[Any, Any]) -> str:
                
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

**get_headers()**
Adds restconf specific headers to a dict
Parameters:
            restconf: which restconf headers should be set
            headers: which additional headers should be set
        Returns:
            dict: The header information
```python            
    def get_headers(self, format: RestconfFormat, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        
        
        restconf_headers = self.headers_json if format == RestconfFormat.JSON else self.headers_xml
        if headers and isinstance(headers, dict):
            return dict(headers, **restconf_headers)
        return dict(restconf_headers)
```

# Contributors
- Julian Klaiber (<julian.klaiber@hsr.ch>)
- Severin Dellsperger (<severin.dellsperger@hsr.ch>)

# Example
Here is an example how do you can configure two different devices:
```
- hostname: RT-6
  username: python
  password: cisco
  connection_address: 10.3.255.106
  interfaces:
    - name: 1
      ip: 10.3.255.106
      mask: 255.255.255.0
      loopback: false
    - name: 0
      ip: 6.6.6.6
      mask: 255.255.255.255
      loopback: true
    - name: 1
      ip: 192.168.6.1
      mask: 255.255.255.0
      loopback: true
  ospf: 
    process_id: 1
    areas:
    - area_id: 0
      networks:
      - 6.6.6.6: 0.0.0.0
      - 192.168.6.0: 0.0.0.255
      - 10.3.255.0: 0.0.0.255
    router_id: 6.6.6.6
    passive_interfaces:
    - lo1
  bgp:
    as_number: 6
    networks:
    - 192.168.6.0: 255.255.255.0 
    neighbors:
    - address: 20.20.20.20
      remote_as: 20
      multihop_count: 2
      update_source:
        loopback: true
        id: 0
    - address: 7.7.7.7
      remote_as: 7
      multihop_count: 3
      update_source:
        loopback: true
        id: 0
- hostname: RT-7
  username: python
  password: cisco
  connection_address: 10.3.255.107
  interfaces:
    - name: 1
      ip: 10.3.255.107
      mask: 255.255.255.0
      loopback: false
    - name: 0
      ip: 7.7.7.7
      mask: 255.255.255.255
      loopback: true
    - name: 1
      ip: 192.168.7.1
      mask: 255.255.255.0
      loopback: true
  ospf: 
    process_id: 1
    areas:
    - area_id: 0
      networks:
      - 7.7.7.7: 0.0.0.0
      - 192.168.7.0: 0.0.0.255
      - 10.3.255.0: 0.0.0.255
    router_id: 7.7.7.7
    passive_interfaces:
    - lo1
  bgp:
    as_number: 7
    networks:
    - 192.168.7.0: 255.255.255.0 
    neighbors:
    - address: 6.6.6.6
      remote_as: 6
      multihop_count: 3
      update_source:
        loopback: true
        id: 0
    - address: 20.20.20.20
      remote_as: 20
      multihop_count: 2
      update_source:
        loopback: true
        id: 0
```