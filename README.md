# GraphQL XML Query Service

A simple GraphQL interface to query values from an XML document shaped according to the OrderViewRS.xsd schema.
A sample XML file is included under sample_xml/.

### Features:
- Fetch the complete XML document as a raw string
- Query nested XML elements using dot-separated paths
- Extract XML attribute values
- Handles nested and repeated XML structures
- Schema-aligned with `OrderViewRS.xsd`
- Simple and extensible GraphQL API design

### How to Run:
1. Activate virtual environment  
   ```bash
   source .venv/bin/activate
2. Install dependencies
   ```bash
   pip install -r requirements.txt
4. Run service
   ```bash
   python3 xml_query_service.py


### Query format:
Query nested XML elements
```
query {
  queryXml(path: "OrderViewRS.Response.Orders.Order.Customer.Name") {
    result
    note
  }
}
```
Query XML attributes
```
query {
  queryXml(
    path: "OrderViewRS.Response.Orders.Order",
    attribute: "OrderID"
  ) {
    result
    note
  }
}
```

### GraphQL Endpoint:
http://127.0.0.1:5000/graphql

## Project Structure 

```
graphql-xml-parser-api/
├── xml_query_service.py
├── requirements.txt
├── sample_xml/
│   └── OrderViewRS_sample.xml
└── README.md

```

