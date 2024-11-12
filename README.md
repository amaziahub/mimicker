<p align="center">
  <img src="mockingbird.jpg" alt="Mockingbird logo" 
       style="width: 200px; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border: 2px solid black;">
</p>
<div>

<div align="center">

> **Mockingbird** – Your lightweight, Python-native HTTP mocking server.

</div>

<div align="center">

[![Mockingbird Tests](https://github.com/amaziahub/mockingbird/actions/workflows/test.yml/badge.svg)](https://github.com/amaziahub/mockingbird/actions/workflows/test.yml)
[![License](http://img.shields.io/:license-apache2.0-red.svg)](http://doge.mit-license.org)
![Poetry](https://img.shields.io/badge/managed%20with-poetry-blue)

</div>
</div>


Mockingbird is a Python-native HTTP mocking server inspired by WireMock, designed to simplify the process of stubbing and
mocking HTTP endpoints for testing purposes.
Mockingbird requires no third-party libraries and is lightweight, making it ideal for integration testing, local
development, and CI environments.

## Features

- Create HTTP stubs for various endpoints and methods
- Mock responses with specific status codes, headers, and body content
- Flexible configuration for multiple endpoints

## Installation

Mockingbird can be installed directly from PyPI using pip or Poetry:

### Using pip:

```bash
pip install mockingbird
```

### Using poetry:

```bash
poetry add mockingbird
```

## Usage

To start Mockingbird on a specific port with a simple endpoint, you can use the following code snippet:

```python
from mockingbird.mockingbird import mockingbird, get

mockingbird(8080).routes(
    get("/hello").
    body({"message": "Hello, World!"}).
    status(200)
)
```

### Examples

#### Using Path Parameters

Mockingbird can handle path parameters dynamically. Here's how you can mock an endpoint with a variable in the path:

```python
from mockingbird.mockingbird import mockingbird, get

mockingbird(8080).routes(
    get("/hello/{name}")
    .body({"message": "Hello, {name}!"})
    .status(200)
)

# When the client sends a request to /hello/world, the response will be:
# {"message": "Hello, world!"}
```

#### Using Headers

You can also mock responses with custom headers:

```python
from mockingbird.mockingbird import mockingbird, get

mockingbird(8080).routes(
    get("/hello")
    .body("Hello with headers")
    .headers([("Content-Type", "text/plain"), ("Custom-Header", "Value")])
    .status(200)
)

# The response will include custom headers
```

#### Multiple Routes

Mockingbird allows you to define multiple routes for different HTTP methods and paths. Here's an example with `GET`
and `POST` routes:

```python
from mockingbird.mockingbird import mockingbird, get, post

mockingbird(8080).routes(
    get("/greet")
    .body({"message": "Hello, world!"})
    .status(200),

    post("/submit")
    .body({"result": "Submission received"})
    .status(201)
)

# Now the server responds to:
# GET /greet -> {"message": "Hello, world!"}
# POST /submit -> {"result": "Submission received"}

```

#### Handling Different Status Codes

You can also mock different HTTP status codes for the same endpoint:

```python
from mockingbird.mockingbird import mockingbird, get

mockingbird(8080).routes(
    get("/status")
    .body({"message": "Success"})
    .status(200),

    get("/error")
    .body({"message": "Not Found"})
    .status(404)
)

# GET /status -> {"message": "Success"} with status 200
# GET /error -> {"message": "Not Found"} with status 404
```

#### Mocking Responses with JSON Body

Mockingbird supports JSON bodies, making it ideal for API testing:

```python
from mockingbird.mockingbird import mockingbird, get

mockingbird(8080).routes(
    get("/json")
    .body({"message": "Hello, JSON!"})
    .status(200)
)

# The response will be: {"message": "Hello, JSON!"}
```

#### Supporting Other Body Types (Text, Files, etc.)

In addition to JSON bodies, Mockingbird supports other types of content for the response body. Here's how you can return
text or file content:

##### Text Response:

```python
from mockingbird.mockingbird import mockingbird, get

mockingbird(8080).routes(
    get("/text")
    .body("This is a plain text response")
    .status(200)
)

# The response will be plain text: "This is a plain text response"
```

#### File Response:

You can also return files from a mock endpoint:

```python
from mockingbird.mockingbird import mockingbird, get

mockingbird(8080).routes(
    get("/file")
    .body(open("example.txt", "rb").read())  # Mock a file response
    .status(200)
)

# The response will be the content of the "example.txt" file

```

## Available Features:

* `get(path)`: Defines a `GET` endpoint.
* `post(path)`: Defines a `POST` endpoint.
* `put(path)`: Defines a `PUT` endpoint.
* `delete(path)`: Defines a `DELETE` endpoint.
* `.body(content)`: Defines the response `body`.
* `.status(code)`: Defines the response `status code`.
* `.headers(headers)`: Defines response `headers`.

## Requirements
Mockingbird supports Python 3.7 and above.


## License
Mockingbird is released under the MIT License. see the [LICENSE](LICENSE) for more information.