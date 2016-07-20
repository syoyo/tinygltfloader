#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import re
import json
from string import Template

def CommaSepStringArray(lst):
    ss = ""
    for (i, e) in enumerate(lst):
        ss += "\"" + e + "\"" 
        if i != (len(lst) - 1):
            ss += ", "
    return ss


def genParseStingProperty(title, propname, description, enum_list, default):
    body = '''

    bool ParseStringProperty(std::string *s, std::string *err, picojson::object &o)
    {
        if (!s) return false;
        (*s) = "${default}";

        if (err) {
            (*err) = "aa"; 
        }

        return true;
    }
    '''

    print(description)

    print(enum_list)
    if enum_list is not None:
        ss = "{\n"
        ss = "const char *enum_lists[] = {" + CommaSepStringArray(enum_list) + "};\n"
        ss += "bool enum_check = false;\n"
        ss += "for (int i = 0; i < sizeof(enum_lists); i++) {\n"
        ss += "  if (value.compare(enum_lists[i]) == 0) enum_check = true\n"
        ss += "}\n"
        ss += "if (!enum_check) goto fail;\n"
        ss += "(*err) = \"Got \" <<  value << \", but Expected value is one of the following enums: [" + re.sub('"', '\\"', CommaSepStringArray(enum_list)) + "] in `" + title + "." + propname + "'\" << std::endl;\n"
        ss += "}\n"
        print(ss)


    d = {}
    d['default'] = default
    s = Template(body)
    code = s.safe_substitute(d)

    print(code)


def main():

    if len(sys.argv) < 2:
        print("Need input.schema.json")
        sys.exit(-1)

    root = json.loads(open(sys.argv[1]).read())
    print(root['title'])

    assert(root['type'] == 'object')

    description = root['description']
    properties = root['properties']
    for prop in properties:
        p = properties[prop]
        if p['type'] == "string":
            genParseStingProperty(root['title'], prop, description, p['enum'] if p.has_key('enum') else None, "bora")


main()

