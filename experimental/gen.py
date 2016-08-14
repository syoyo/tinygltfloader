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

def typeToString(ty):
    if ty == "string":
        return "std::string"
    elif ty == "integer":
        return "int64_t"
    elif ty == "number":
        return "double"
    else:
        raise

def emitStruct(title, properties):
    s = "typedef struct {\n"
    for prop_name in properties:
        p = properties[prop_name]
        if p.has_key('type'):
            s += typeToString(p['type']) + " " + prop_name + ";\n"
    s += '} ' + title + ';\n'

    return s

def genParseIntProperty(title, propname, prop):
    s = ""
    s += 'bool Parse_${propname}(int64_t *s, std::string *err, picojson::object &o) {\n'
    s += '  if (!s) return false; \n'
    s += '  std::stringstream ss; \n'
    s += '  int64_t value;\n'
    s += '  picojson::object::const_iterator it = o.find("${propname}");\n'
    s += '\n'

    if prop.has_key('required') and prop['required'] == True:
        s += '  if (it == o.end()) {;\n'
        s += '    ss << "\\"${propname}\\" is a required field but missing in `${title}\' property" << std::endl;\n'
        s += '    goto fail;\n'
        s += '  }\n'
    else:
        if prop.has_key('default'):
            s += '  value = ${default};\n'
        s += '  if (it != o.end()) {\n'
        s += '    if (!(it->second.is<double>())) {\n'
        s += '      ss << "\\"${propname}\\" field is not a integer type" << std::endl;\n'
        s += '      goto fail;\n'
        s += '    }\n'     
        s += '    value = it->second.get<double>();\n'
        s += '  }\n'

    if prop.has_key('minimum'):
        min_value = int(prop['minimum'])
        ss  = "{\n"
        ss += "  const int64_t min_value = {0};\n".format(min_value) 
        ss += "  if (value < min_value) {\n"
        ss += "    ss << \"Got \" <<  value << \", but minimum value alloed is \" << min_value << std::endl;\n"
        ss += "    goto fail;\n"
        ss += "  }\n"
        ss += "}\n"
        print(ss)

        s += ss 

    s += '\n'
    s += '  return true;\n'
    s += 'fail:\n'
    s += '  if (err) {\n'
    s += '    (*err) = ss.str();\n'
    s += '  };\n'
    s += '  return false;\n'
    s += '}\n'
    s += '\n'

    d = {}
    if prop.has_key('default'):
        d['default'] = prop['default']
    d['propname'] = propname
    d['title'] = title
    ts = Template(s)
    code = ts.safe_substitute(d)

    return code

def genParseStingProperty(title, propname, prop):
    s = ""
    s += 'bool Parse_${propname}(std::string *s, std::string *err, picojson::object &o) {\n'
    s += '  if (!s) return false; \n'
    s += '  std::stringstream ss; \n'
    s += '  std::string value;\n'
    s += '  picojson::object::const_iterator it = o.find("${propname}");\n'
    s += '\n'

    if prop.has_key('required') and prop['required'] == True:
        s += '  if (it == o.end()) {;\n'
        s += '    ss << "\\"${propname}\\" is a required field but missing in `${title}\' property" << std::endl;\n'
        s += '    goto fail;\n'
        s += '  }\n'
    else:
        if prop.has_key('default'):
            s += '  value = "${default}";\n'
        s += '  if (it != o.end()) {\n'
        s += '    if (!(it->second.is<std::string>())) {\n'
        s += '      ss << "\\"${propname}\\" field is not a string type" << std::endl;\n'
        s += '      goto fail;\n'
        s += '    }\n'     
        s += '    value = it->second.get<std::string>();\n'
        s += '  }\n'

    if prop.has_key('enum'):
        enum_list = prop['enum']
        ss  = "{\n"
        ss += "  const char *enum_lists[] = {" + CommaSepStringArray(enum_list) + "};\n"
        ss += "  bool enum_check = false;\n"
        ss += "  for (int i = 0; i < sizeof(enum_lists); i++) {\n"
        ss += "    if (value.compare(enum_lists[i]) == 0) enum_check = true;\n"
        ss += "  }\n"
        ss += "  if (!enum_check) {\n"
        ss += "    ss << \"Got \" <<  value << \", but Expected value is one of the following enums: [" + re.sub('"', '\\"', CommaSepStringArray(enum_list)) + "] for `" + title + "." + propname + "'\" << std::endl;\n"
        ss += "    goto fail;\n"
        ss += "  }\n"
        ss += "}\n"
        print(ss)

        s += ss 

    s += '\n'
    s += '  return true;\n'
    s += 'fail:\n'
    s += '  if (err) {\n'
    s += '    (*err) = ss.str();\n'
    s += '  };\n'
    s += '  return false;\n'
    s += '}\n'
    s += '\n'

    d = {}
    if prop.has_key('default'):
        d['default'] = prop['default']
    d['propname'] = propname
    d['title'] = title
    ts = Template(s)
    code = ts.safe_substitute(d)

    return code


def main():

    if len(sys.argv) < 2:
        print("Need input.schema.json")
        sys.exit(-1)

    root = json.loads(open(sys.argv[1]).read())
    print(root['title'])

    assert(root['type'] == 'object')

    description = root['description']
    properties = root['properties']
    s = ""

    s += "#include <string>\n"
    s += "#include <sstream>\n"
    s += "#include \"picojson.h\"\n"

    s += emitStruct(root['title'], properties)

    for prop in properties:
        p = properties[prop]
        if p.has_key('type'):
            if p['type'] == "string":
                s += genParseStingProperty(root['title'], prop, p)
            elif p['type'] == "integer":
                s += genParseIntProperty(root['title'], prop, p)

    f = open('output.cc', 'w')
    f.write(s)
    f.close()

main()

