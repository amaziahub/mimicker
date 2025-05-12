<p align="center">
  <img src="https://raw.githubusercontent.com/amaziahub/mimicker/main/mimicker.jpg" alt="Mimicker logo" 
       style="width: 200px; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border: 2px solid black;">
</p>
<div>

<div align="center">

> **Mimicker** – Your lightweight, Python-native HTTP mocking server.

</div>

<div align="center">

[![Mimicker Tests](https://github.com/amaziahub/mimicker/actions/workflows/test.yml/badge.svg)](https://github.com/amaziahub/mimicker/actions/workflows/test.yml)
[![PyPI Version](https://img.shields.io/pypi/v/mimicker.svg)](https://pypi.org/project/mimicker/)
[![Downloads](https://pepy.tech/badge/mimicker)](https://pepy.tech/project/mimicker)
[![Last Commit](https://img.shields.io/github/last-commit/amaziahub/mimicker.svg)](https://github.com/amaziahub/mimicker/commits/main)
[![Codecov Coverage](https://codecov.io/gh/amaziahub/mimicker/branch/main/graph/badge.svg?token=YOUR_CODECOV_TOKEN)](https://codecov.io/gh/amaziahub/mimicker)
[![License](http://img.shields.io/:license-apache2.0-red.svg)](http://doge.mit-license.org)
![Poetry](https://img.shields.io/badge/managed%20with-poetry-blue)

</div>
</div>


Mimicker is a Python-native HTTP mocking server inspired by WireMock, designed to simplify the process of stubbing and
mocking HTTP endpoints for testing purposes.
Mimicker requires no third-party libraries and is lightweight, making it ideal for integration testing, local
development, and CI environments.

## Features

- Create HTTP stubs for various endpoints and methods
- Mock responses with specific status codes, headers, and body content
- Flexible configuration for multiple endpoints

## Installation

Mimicker can be installed directly from PyPI using pip or Poetry:

### Using pip:

```bash
pip install mimicker
```

### Using poetry:

```bash
poetry add mimicker
```

## Usage

To start Mimicker on a specific port with a simple endpoint, you can use the following code snippet:

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/hello").
    body({"message": "Hello, World!"}).
    status(200)
)
```

### Examples

#### Using Path Parameters

Mimicker can handle path parameters dynamically. Here's how you can mock an endpoint with a variable in the path:

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/hello/{name}")
    .body({"message": "Hello, {name}!"})
    .status(200)
)

# When the client sends a request to /hello/world, the response will be:
# {"message": "Hello, world!"}
```

#### Using Query Parameters

##### Explicitly defined query parameters

Mimicker can handle query parameters dynamically. Here's how you can mock an endpoint with a variable in the query:

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/hello?name={name}")
    .body({"message": "Hello, {name}!"})
    .status(200)
)

# When the client sends a request to /hello?name=world, the response will be:
# {"message": "Hello, world!"}
```

##### Implicit query parameters

When query parameters are not explicitly part of the path template, Mimicker will match
all otherwise matching requests against those parameters as if using a wildcard. For instance

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/hello")
    .body({"message": "Hello, world!"})
    .status(200)
)

# When the client sends a request to /hello?name=bob, the request will match and the response will be:
# {"message": "Hello, world!"}
```

These implicitly matched query parameters are available through dynamic responses
using the `"query_params"` key in `kwargs` in `response_func` (see below), e.g.

```python
from mimicker.mimicker import mimicker, get

def custom_response(**kwargs):
    query_params: Dict[str, List[str]] = kwargs['query_params']
    return 200, {"message": f"Hello {query_params['name'][0]}!"}

mimicker(8080).routes(
    get("/hello")
    .response_func(custom_response)
)

# When the client sends a request to /hello?name=world, the request will match and the response will be:
# {"message": "Hello, world!"}
```

Note that because query parameters can be repeated with multiple values, they will
always appear in a list of values.

#### Using Headers

You can also mock responses with custom headers:

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/hello")
    .body("Hello with headers")
    .headers([("Content-Type", "text/plain"), ("Custom-Header", "Value")])
    .status(200)
)

# The response will include custom headers
```

#### Multiple Routes

Mimicker allows you to define multiple routes for different HTTP methods and paths. Here's an example with `GET`
and `POST` routes:

```python
from mimicker.mimicker import mimicker, get, post

mimicker(8080).routes(
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
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
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

Mimicker supports JSON bodies, making it ideal for API testing:

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/json")
    .body({"message": "Hello, JSON!"})
    .status(200)
)

# The response will be: {"message": "Hello, JSON!"}
```

#### Delaying the response

This is useful when testing how your code handles timeouts when calling a web API.

```python
from mimicker.mimicker import mimicker, get
import requests

mimicker(8080).routes(
    get("/wait").
    delay(0.5).
    body("the client should have timed out")
)
try:
    resp = requests.get("http://localhost:8080/wait", timeout=0.2)
except requests.exceptions.ReadTimeout as error:
    print(f"the API is unreachable due to request timeout: {error=}")
else:
    # do things with the response
    ...
```

#### Supporting Other Body Types (Text, Files, etc.)

In addition to JSON bodies, Mimicker supports other types of content for the response body. Here's how you can return
text or file content:

##### Text Response:

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/text")
    .body("This is a plain text response")
    .status(200)
)

# The response will be plain text: "This is a plain text response"
```

#### File Response:

You can also return files from a mock endpoint:

```python
from mimicker.mimicker import mimicker, get

mimicker(8080).routes(
    get("/file")
    .body(open("example.txt", "rb").read())  # Mock a file response
    .status(200)
)

# The response will be the content of the "example.txt" file

```

### Dynamic Responses with `response_func`

Mimicker allows dynamic responses based on the request data using `response_func`. 
This feature enables you to build mock responses that adapt based on request parameters, headers, and body.

```python
from mimicker.mimicker import mimicker, post

# Available for use with response_func:
# kwargs.get("payload")
# kwargs.get("headers")
# kwargs.get("params")

def custom_response(**kwargs):
    request_payload = kwargs.get("payload")
    return 200, {"message": f"Hello {request_payload.get('name', 'Guest')}"}

mimicker(8080).routes(
    post("/greet")
    .response_func(custom_response)
)

# POST /greet with body {"name": "World"} -> {"message": "Hello World"}
# POST /greet with empty body -> {"message": "Hello Guest"}
```


## Available Features:

* `get(path)`: Defines a `GET` endpoint.
* `post(path)`: Defines a `POST` endpoint.
* `put(path)`: Defines a `PUT` endpoint.
* `delete(path)`: Defines a `DELETE` endpoint.
* `patch(path)`: Defines a `PATCH` endpoint.
* `.delay(duration)`: Defines the delay in seconds waited before returning the response (optional, 0. by default).
* `.body(content)`: Defines the response `body`.
* `.status(code)`: Defines the response `status code`.
* `.headers(headers)`: Defines response `headers`.
* `.response_func(func)`: Defines a dynamic response function based on the request data.

---

## Logging
Mimicker includes built-in logging to help you observe and debug how your mocked endpoints behave.

By default, Mimicker logs at the INFO level and uses a colorized output for readability. You’ll see messages like:

```css
[MIMICKER] [2025-05-04 14:52:10] INFO: ✓ Matched stub. Returning configured response.
```

and:

```css
[MIMICKER] [2025-05-05 11:50:10,226] INFO: → GET /hello
Headers:
{
  "host": "localhost:8080",
  "user-agent": "python-requests/2.31.0",
  "accept-encoding": "gzip, deflate",
  "accept": "*/*",
  "connection": "keep-alive"
}
```

###  Controlling the Log Level
You can control the log level using the `MIMICKER_LOG_LEVEL` environment variable. Valid values include:

- `DEBUG`
- `INFO` (default)
- `WARNING`
- `ERROR`
- `CRITICAL`

This will show detailed request information including method, path, headers, and body.

---

## Requirements
Mimicker supports Python 3.7 and above.

---

### Get in touch

You are welcome to report 🐞 or  [issues](https://github.com/amaziahub/mimicker/issues),
upvote 👍 [feature requests](https://github.com/users/amaziahub/projects/1),
or 🗣️ discuss features and ideas @ [slack community](https://join.slack.com/t/mimicker/shared_invite/zt-2yr7vubw4-8Y09YyxZ5j~G2tlQ5uOXKw)


### Contributors

I'm thankful to all the people who have contributed to this project.

<a href="https://github.com/amaziahub/mimicker/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=amaziahub/mimicker" />
</a>


## License
Mimicker is released under the MIT License. see the [LICENSE](LICENSE) for more information.