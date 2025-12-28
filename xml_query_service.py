import os
import json
from flask import Flask, request, jsonify
import graphene
import xmltodict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XML_PATH = os.path.join(BASE_DIR, "sample_xml", "OrderViewRS_sample.xml")

# loading and parsing the xml
def load_xml_as_dict():
    if not os.path.exists(XML_PATH):
        return None
    with open(XML_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return xmltodict.parse(content, force_list=None)

def _navigate_path(data, parts):
    cur = data
    for p in parts:
        if cur is None:
            return None
        if isinstance(cur, list):
            nexts = []
            for item in cur:
                if isinstance(item, dict) and p in item:
                    nexts.append(item[p])
            cur = nexts or None
        elif isinstance(cur, dict):
            cur = cur.get(p)
        else:
            return None
    return cur

def extract_attribute(node, attr_name):
    if node is None:
        return None
    results = []

    def _get_attr_from_obj(obj):
        if isinstance(obj, dict):
            if attr_name in obj:
                return obj[attr_name]
            alt = "@" + attr_name
            if alt in obj:
                return obj[alt]
        return None

    if isinstance(node, list):
        for item in node:
            val = _get_attr_from_obj(item)
            if val is not None:
                results.append(val)
    else:
        val = _get_attr_from_obj(node)
        if val is not None:
            results.append(val)

    if not results:
        return None
    if len(results) == 1:
        return results[0]
    return results

# GraphQl types are written here
class XmlResult(graphene.ObjectType):
    result = graphene.String()
    note = graphene.String()

class Query(graphene.ObjectType):
    rawXml = graphene.String()
    # path example: "OrderViewRS.Orders.Order" (dot-separated) for querying
    queryXml = graphene.Field(XmlResult,
                              path=graphene.String(required=True),
                              attribute=graphene.String())  # optional attribute name

    def resolve_rawXml(root, info):
        if not os.path.exists(XML_PATH):
            return None
        with open(XML_PATH, "r", encoding="utf-8") as f:
            return f.read()

    def resolve_queryXml(root, info, path, attribute=None):
        data = load_xml_as_dict()
        if not data:
            return XmlResult(result=None, note="XML file not found")
        parts = [p for p in path.split(".") if p]

        node = _navigate_path(data, parts)
        if node is None:
            return XmlResult(result=None, note="Path not found")
        if attribute:
            attr_val = extract_attribute(node, attribute)
            if attr_val is None:
                return XmlResult(result=None, note=f"Attribute '{attribute}' not found at path")
            return XmlResult(result=json.dumps(attr_val, indent=2), note=f"Attribute '{attribute}'")
        return XmlResult(result=json.dumps(node, indent=2), note="OK")

schema = graphene.Schema(query=Query, auto_camelcase=False)

# implementing the Flask app
app = Flask(__name__)

@app.route("/graphql", methods=["POST"])
def graphql_endpoint():
    payload = request.get_json(force=True)
    query = payload.get("query")
    variables = payload.get("variables")
    result = schema.execute(query, variable_values=variables)
    response = {"data": result.data if result.data is not None else None}
    if result.errors:
        errors_out = []
        for err in result.errors:
            err_obj = {"message": str(err)}
            if hasattr(err, "locations") and err.locations:
                err_obj["locations"] = [{"line": loc.line, "column": loc.column} for loc in err.locations]
            if hasattr(err, "path") and err.path:
                err_obj["path"] = err.path
            errors_out.append(err_obj)
        response["errors"] = errors_out
    return jsonify(response)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "XML Query GraphQL service running. POST GraphQL to /graphql"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
