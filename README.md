# Mockingbird

## Features
Create HTTP stubs for various endpoints and methods
Mock responses with specific status codes, headers, and body content
Flexible configuration for multiple endpoints
Built entirely with standard Python libraries

### Installation
To get started, clone the repository and install dependencies using pip:

```bash
git clone https://github.com/amaziahub/mockingbird
cd mockingbird
pip install -r requirements.txt
```
Usage
To start Mockingbird on a specific port with a simple endpoint, you can use the following code snippet:

```python
from mockingbird import serve

# Start server and define an endpoint
serve(8080).get('/example', response={"message": "Hello, Mockingbird!"})
```

### Running Tests
To run tests, simply use pytest:

```bash
pytest
```

### Requirements
Mockingbird has no external runtime dependencies. Development and testing dependencies include:

* pytest
* PyHamcrest 
* requests 
* flake8

### License
Mockingbird is released under the MIT License. See LICENSE for more information.