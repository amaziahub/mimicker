# Mockingbird
[![Mockingbird Tests](https://github.com/amaziahub/mockingbird/actions/workflows/test.yml/badge.svg)](https://github.com/amaziahub/mockingbird/actions/workflows/test.yml)

Mokingbird is a Python-native HTTP mocking server inspired by WireMock, designed to simplify the process of stubbing and mocking HTTP endpoints for testing purposes.
Mokingbird requires no third-party libraries and is lightweight, making it ideal for integration testing, local development, and CI environments.

<p align="center">
  <img src="mockingbird.jpg" alt="Mockingbird logo">
</p>


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
from mockingbird.mockingbird import mockingbird, get

mockingbird(8080).routes(
    get("/hello").
    body({"message": "Hello, World!"}).
    status(200)
)
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