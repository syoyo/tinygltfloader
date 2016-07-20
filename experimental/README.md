# Simple C++ parser code generator from JSON schema.

## Strategy

Use python to generate c++ code from JSON schema.
Apply clang-format for code formatting.
Use picojson as a JSON library in C++.

## Requirements

* Python 2.7+

## Gen code

    $ python gen.py input.schema.json


## TODO

* [ ] Validate input JSON schema.
