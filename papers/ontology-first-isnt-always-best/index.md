*Why should we discourage an ontology-first approach (whereby a comprehensive enterprise-level collaborative ontology is used), and instead use a federated incremental approach to integrate data from various systems?*

> Note: A good context and example of federated approach (for upper-meta alignment) is Netflix's Unified Data Architecture (UDA) [link], which we will see referenced in this discussion.

## 1. The Ontology-First Temptation

In traditional "enterprise ontology" programs (often seen in healthcare, manufacturing, or large corporate data initiatives):

- The assumption is that a single, comprehensive ontology can be collaboratively engineered up front.
- Every system and dataset will map to this canonical ontology before integration.
- The ontology is treated like a schema-of-truth; a stable, agreed-upon conceptual model.

Problems with that assumption:

- Real systems often evolve asynchronously and use different identity and modeling conventions (e.g., RDBMS normalized IDs, Excel textual labels, GraphQL JSON conventions).
- Each subsystem has its own performance and business semantics; e.g., GraphQL focuses on application-level resolvers and typed responses; Excel is human-centric and flexible; RDBMS focuses on atomic integrity.
- Enforcing a unified ontology upfront creates a choke point; integration work is delayed until consensus is reached.
- The ontology itself becomes a bottleneck because every change requires enterprise-wide coordination.

## 2. Developing a Minimal Example as a Reality Check

We will develop a small "MBSE" example that attempts to demonstrate this tension concretely, in particular for situations we often see across enterprise (e.g. DoD) and/or industries (e.g. MBSE). In these situations, different data sources, systems, etc. already exist and it is desired to provide integration for the system view (or system-of-systems, etc.).

| Source | Strength | Weakness | Ontology alignment issue |
|---|---|---|---|
| RDBMS/GraphQL | High structural consistency, strong typing, good URIs | Localized domain naming (GraphQL patterns like `/Component/COMP-1`) | Aligns well with ontology, but introduces unique ID pattern |
| Excel | Rapid flexibility, low barrier for entry | Loose structure, semantic drift ("FlightControl" vs "Flight Control") | Violates ontology shapes (no `ex:hasPart`, inconsistent identifiers) |

What this shows is:

- Each data source embodies different modeling cultures.
- Forcing both to conform to a single "perfect" ontology up front would erode the value of those local optimizations.

So rather than designing a monolithic ontology first, you overlay the ontology gradually, using validation and alignment (e.g., SHACL) to detect mismatches and progressively improve integration fidelity.

## 3. The Federated, Incremental Approach

The system's architecture (OWL + SHACL + mappings) naturally supports a federated ontology ecosystem, not a top-down ontology regime.

### A. Core Principles

1. **Each domain or system retains local autonomy.** The RDBMS continues using its GraphQL-resolved schema. The Excel system remains flexible and user-driven. The ontology layer doesn't force either system to change its operational data model.
2. **Ontology becomes a "bridge language" (i.e. lingua franca), not a master schema.** Instead of owning the data model, it provides a semantic bridge (URI patterns, predicates, and classes). Systems map to the ontology at the boundary; when publishing RDF or interacting with the knowledge graph.
3. **Validation replaces prescription.** SHACL doesn't prescribe how the system should store data; it just validates exported RDF. This encourages incremental conformance: teams can align progressively, guided by validation feedback rather than a global schema rewrite.
4. **Integration is driven by reconciliation, not uniformity.** Instead of assuming uniform semantics, reconciliation logic (e.g., `owl:sameAs`, canonical ID mappings, or subproperty bridges) links entities dynamically.

### B. Technical Dynamics

- Each system publishes its own RDF graph.
- A shared ontology defines core conceptual anchors (`ex:Component`, `ex:Part`, `ex:hasPart`).
- SHACL shapes express minimal interoperability expectations (what's required for cross-system reasoning).
- A federated query layer (SPARQL service federation, or graph federation middleware) merges and reasons over multiple data sources on-demand.

Thus, ontology conformance is enforced at query-time or ingest-time, not pre-imposed on source systems.

## 4. Analogy: Netflix's Unified Data Architecture (UDA)

Netflix's data ecosystem follows a similar logic:

- Each system (microservice, dataset, event stream) owns its schema; there is no global canonical model.
- Metadata is harvested into a knowledge layer where schemas are described, related, and searchable.
- The "unification" happens through contracts and metadata interoperability, not forced schema uniformity.

> Note: the focus for UDA is to make metadata interoperable and discoverable so that the enterprise can say "we are modeling Concept XYZ in 'such and such' way across these various systems, and each contains exactly this data within it." This is more of a metadata integration and data traceability problem as opposed to trying to align services to utilize e.g. the same "Authoritative Source of Truth".

In our RDF + SHACL analogy:

- RDF/OWL ontology ≈ the minimal common language
- SHACL ≈ data contract validation and quality rules
- Individual systems' graphs ≈ autonomous microservices datasets
- Federated SPARQL queries ≈ data mesh or metadata APIs, which retrieve unified results without collapsing autonomy.

## 5. Why This System Disincentivizes the Ontology-First Model

| Ontology-First (Monolithic) | Federated Incremental (OWL + SHACL Model) |
|---|---|
| Requires up-front agreement on all classes, properties, and constraints | Allows gradual convergence through SHACL validations |
| Coupled tightly to source systems' implementation | Decoupled via RDF serialization and validation layer |
| Slow to adapt to schema drift | Adaptable: SHACL shapes can evolve independently |
| Breaks local optimizations (e.g., GraphQL resolvers, RDBMS normalization) | Preserves local strengths while harmonizing at the semantic edge |
| Ontology changes are centralized governance bottlenecks | Ontology acts as a stable core with modular extensions per domain |

The validation-driven integration approach turns ontology development into a living process; guided by where mismatches actually occur in real data, not by hypothetical enterprise models. The ontology and SHACL layer mediate, not dominate. Integration happens from the edges inward, not from the top down.

> Note: similar to some high-end enterprise knowledge graph solutions (i.e. Stardog) the RDF export may be replaced with e.g. "virtualization" wherein the central services SPARQL service is capable of converting portions of queries (i.e. `SELECT FROM <virtual-graph>`) into queries for the specific service, thereby reducing the burden of maintaining data copies in the central knowledge system.

## 6. The Payoff

- **Scalable Governance:** Ontology governance is distributed; each domain evolves its mappings locally.
- **Organic Convergence:** Repeated SHACL validation and SPARQL integration tests reveal real convergence points; ontology growth follows data reality.
- **Ecosystem Resilience:** Systems can evolve independently (Excel can change tomorrow, GraphQL can evolve its schema) as long as they continue publishing valid RDF and pass SHACL validation.
- **Emergent Enterprise Ontology:** Over time, the ontology becomes a reflection of working integrations, not a speculative design artifact.

## Summary

The system discourages an ontology-first (top-down) strategy because:

- Real-world data systems differ in schema maturity and pace.
- SHACL validation and federated RDF mapping make it possible to integrate as-is datasets while progressively improving conformance.

This inversion, ontology as a reference instead of a prescription, turns integration into an iterative, feedback-driven process. Much like Netflix's Unified Data Architecture:

> "Data unification doesn't mean schema unification; it means discoverability, validation, and interoperability while preserving autonomy."

## Demo: Utilizing SHACL (+/- ontology) to validate federated data sources

End-to-end example that demonstrates why OWL alone isn't enough and how SHACL helps detect missing links when two data silos (an RDBMS exposed through GraphQL, and a loosely-structured Excel file) both claim to use the same ontology but, because of implementation patterns, they produce missed connections in the integrated knowledge graph.

The example includes:

- A small RDBMS dataset and a Python init that maps its GraphQL view -> RDF (Turtle).
- A small Excel dataset, its loose schema, and Python mapping -> RDF (Turtle).
- A SPARQL query that shows the mismatch (missing expected connections).
- SHACL NodeShapes for the concepts, showing GraphQL/RDBMS instances validate while the Excel instances fail.
- A fix: aligning the Excel mapping to the SHACL shapes and ontology (e.g., adding `owl:sameAs` or normalizing IDs), which makes the data pass SHACL and causes the earlier SPARQL mismatch to disappear.

### Example domain (MBSE-ish, simplified)

We model a small MBSE slice:

- `ex:Component`; a system/component class.
- `ex:Part`; parts that belong to Components.
- Relationship: `ex:hasPart` from Component to Part.
- Parts have `ex:partNumber` and `ex:partType`.
- Component must have at least one `ex:hasPart` (domain rule we want enforced).

OWL ontology portion (informal): `ex:Component rdfs:subClassOf owl:Thing`, `ex:hasPart rdf:type owl:ObjectProperty`, etc. But the issue arises because of how the two sources implement identifiers and properties.

### 1) RDBMS dataset + GraphQL layer -> RDF

We'll create a small SQLite DB with tables `components` and `parts`. The GraphQL layer exposes Component with `id`, `name`, and `parts` (list of part IDs). The GraphQL implementation normalizes identifiers as URIs like `http://example.org/resource/Component/COMP-<id>` and `http://example.org/resource/Part/PART-<id>`.

Sample records (RDBMS): `components` holds `(1, "FlightControl")`; `parts` holds `(10, 1, "FC-SENSOR-01", "Sensor")` and `(11, 1, "FC-ACT-02", "Actuator")`.

> Note: we inject limited provenance data for tracking example. Ideally provenance would be attached to a named graph or container-like term.

```python
import sqlite3
from rdflib import BNode, Graph, Namespace, URIRef, Literal
from rdflib.namespace import PROV, RDF, RDFS, XSD, OWL

EX = Namespace("http://example.org/ontology/")
RES = Namespace("http://example.org/resource/")

conn = sqlite3.connect("mbse.db")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS components (id INTEGER PRIMARY KEY, name TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS parts (id INTEGER PRIMARY KEY, component_id INTEGER, part_number TEXT, part_type TEXT)")
cur.execute("DELETE FROM components")
cur.execute("DELETE FROM parts")
cur.execute("INSERT INTO components (id,name) VALUES (?,?)", (1, "FlightControl"))
cur.executemany(
    "INSERT INTO parts (id,component_id,part_number,part_type) VALUES (?,?,?,?)",
    [(10, 1, "FC-SENSOR-01", "Sesor"), (11, 1, "FC-ACT-02", "Actuator")]
)
conn.commit()

g1 = Graph()
g1.bind("ex", EX)
g1.bind("res", RES)

g1.add((EX.Component, RDF.type, OWL.Class))
g1.add((EX.Part, RDF.type, OWL.Class))
g1.add((EX.hasPart, RDF.type, OWL.ObjectProperty))
g1.add((EX.partNumber, RDF.type, OWL.DatatypeProperty))
g1.add((EX.partType, RDF.type, OWL.DatatypeProperty))

for cid, name in cur.execute("SELECT id, name FROM components").fetchall():
    comp_uri = URIRef(f"{RES}Component/COMP-{cid}")
    g1.add((comp_uri, RDF.type, EX.Component))
    g1.add((comp_uri, RDFS.label, Literal(name, datatype=XSD.string)))

    for pid, pnum, ptype in conn.execute(
        "SELECT id, part_number, part_type FROM parts WHERE component_id=?", (cid,)
    ).fetchall():
        part_uri = URIRef(f"{RES}Part/PART-{pid}")
        g1.add((part_uri, RDF.type, EX.Part))
        g1.add((part_uri, EX.partNumber, Literal(pnum)))
        g1.add((part_uri, EX.partType, Literal(ptype)))
        g1.add((comp_uri, EX.hasPart, part_uri))
        # part provenance
        rdbms_bnode = BNode()
        g1.add((part_uri, RDF.type, PROV.Entity))
        g1.add((part_uri, PROV.wasDerivedFrom, rdbms_bnode))  # placeholder
        g1.add((rdbms_bnode, RDFS.label, Literal("RDBMS")))

print(g1.serialize(format="turtle"))
```

```turtle
@prefix ex: <http://example.org/ontology/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:hasPart a owl:ObjectProperty .
ex:partNumber a owl:DatatypeProperty .
ex:partType a owl:DatatypeProperty .

<http://example.org/resource/Component/COMP-1> a ex:Component ;
    rdfs:label "FlightControl"^^xsd:string ;
    ex:hasPart <http://example.org/resource/Part/PART-10>,
        <http://example.org/resource/Part/PART-11> .

ex:Component a owl:Class .

<http://example.org/resource/Part/PART-10> a ex:Part,
        prov:Entity ;
    ex:partNumber "FC-SENSOR-01" ;
    ex:partType "Sesor" ;
    prov:wasDerivedFrom [ rdfs:label "RDBMS" ] .

<http://example.org/resource/Part/PART-11> a ex:Part,
        prov:Entity ;
    ex:partNumber "FC-ACT-02" ;
    ex:partType "Actuator" ;
    prov:wasDerivedFrom [ rdfs:label "RDBMS" ] .

ex:Part a owl:Class .
```

> Notes: the GraphQL layer is simulated by using the URI patterns `Component/COMP-<id>` and `Part/PART-<id>`. A real GraphQL layer would produce the same URIs when converting to RDF.

### 2) Excel dataset (loose schema) -> RDF

A different team provides an Excel sheet `legacy_parts.xlsx` with rows like:

| component_name | pnum | type |
|---|---|---|
| Flight Control | FC-SENSOR-01 | Sens |
| FlightControl | FC-GPS-01 | Sensor |

Notice:

- `component_name` values vary in formatting: `"Flight Control"` vs `"FlightControl"`.
- `type` uses inconsistent codes (`"Sens"` vs `"Sensor"`).
- The Excel mapping team naively creates IRIs like `http://example.org/resource/Component/<component_name>` **without normalizing** or matching the GraphQL URIs. They also map parts as literals linked by a property `legacy:belongsTo` (a different property name), or they might just store `component_name` as a string and not create an explicit `ex:hasPart` triple.

```python
import csv
from urllib.parse import quote
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, OWL

EX = Namespace("http://example.org/ontology/")
RES = Namespace("http://example.org/resource/")
LEG = Namespace("http://example.org/legacy/")

g2 = Graph()
g2.bind("ex", EX)
g2.bind("res", RES)
g2.bind("leg", LEG)

# Add lightweight ontology terms if desired
g2.add((EX.Part, RDF.type, OWL.Class))
g2.add((LEG.belongsTo, RDF.type, RDF.Property))

# Read CSV (as stand-in for Excel)
with open("legacy_parts.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        comp_name = row['component_name']  # e.g., "Flight Control"
        pnum = row['pnum']
        ptype = row['type']
        # naive URI construction WITHOUT normalizing or matching GraphQL pattern
        comp_uri = URIRef(f"{RES}Component/{quote(comp_name)}")  # space in URI -> encoded
        part_uri = URIRef(f"{RES}Part/{quote(pnum)}")  # Part URIs here use part_number as identifier
        g2.add((part_uri, RDF.type, EX.Part))
        g2.add((part_uri, EX.partNumber, Literal(pnum)))
        # legacy mapping uses a different property
        g2.add((part_uri, LEG.belongsTo, Literal(comp_name)))  # literally the name string
        g2.add((part_uri, EX.partType, Literal(ptype)))
        # part provenance
        csv_bnode = BNode()
        g2.add((part_uri, RDF.type, PROV.Entity))
        g2.add((part_uri, PROV.wasDerivedFrom, csv_bnode))  # placeholder
        g2.add((csv_bnode, RDFS.label, Literal("CSV")))

# Serialize
print(g2.serialize(format="turtle"))
```

```turtle
@prefix ex: <http://example.org/ontology/> .
@prefix leg: <http://example.org/legacy/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

leg:belongsTo a rdf:Property .

<http://example.org/resource/Part/FC-GPS-01> a ex:Part,
        prov:Entity ;
    leg:belongsTo "FlightControl" ;
    ex:partNumber "FC-GPS-01" ;
    ex:partType "Sensor" ;
    prov:wasDerivedFrom [ rdfs:label "CSV" ] .

<http://example.org/resource/Part/FC-SENSOR-01> a ex:Part,
        prov:Entity ;
    leg:belongsTo "Flight Control" ;
    ex:partNumber "FC-SENSOR-01" ;
    ex:partType "Sens" ;
    prov:wasDerivedFrom [ rdfs:label "CSV" ] .

ex:Part a owl:Class .
```

Key issues introduced by the Excel mapping:

- `leg:belongsTo` is a literal property linking part -> literal component name, not to the `ex:Component` resource used by GraphQL mapping.
- The component naming is inconsistent (`"Flight Control"` vs `"FlightControl"`), and the Excel mapping **didn't normalize IDs**, nor did it create `ex:Component` instances with `ex:hasPart`.
- The Excel mappings produce `res:Part/FC-SENSOR-01` which is not linked via `ex:hasPart` to `res:Component/COMP-1`.

### 3) Integrated knowledge graph with SPARQL query exposing the (logic) mismatch

Assume we merge the two RDF graphs into one merged RDF graph (union of the two Turtle outputs). Now run a SPARQL query that *expects* to find every Part and the Component that owns it (via `ex:hasPart` or, equivalently, find parts belonging to components).

SPARQL query expecting parts and their component URIs (prefers `ex:hasPart`):

```python
from rdf_layer.sparql.framer import SPARQLFramer

class PartComponents(SPARQLFramer):
    """Find Parts and the Component that contains them via ex:hasPart"""
    sparql = """
    SELECT ?part ?partNumber ?source ?component WHERE {
        ?part a ex:Part ;
            ex:partNumber ?partNumber ;
            prov:wasDerivedFrom/rdfs:label ?source .

        # Find components that have the part (the authoritative GraphQL mapping)
        ?component a ex:Component ;
            ex:hasPart ?part .
    }
    """
    initNs = {
        "ex": "http://example.org/ontology/",
        "res": "http://example.org/resource/",
        "prov": PROV,
        "leg": "http://example.org/legacy/"
    }

PartComponents.run_query(g1+g2)
```

| | part | partNumber | source | component |
|---|---|---|---|---|
| 0 | res:Part/PART-11 | FC-ACT-02 | RDBMS | res:Component/COMP-1 |
| 1 | res:Part/PART-10 | FC-SENSOR-01 | RDBMS | res:Component/COMP-1 |

Notes on the result for the merged graph:

- For RDBMS parts `PART-10` and `PART-11`: they are matched because `res:Component/COMP-1 ex:hasPart res:Part/PART-10` etc.
- For Excel parts `res:Part/FC-SENSOR-01` and `res:Part/FC-GPS-01`: **no match**; because there is no `ex:hasPart` linking them to an `ex:Component` URI. Instead, they have `leg:belongsTo` literal strings.

So the query returns only the RDBMS parts; missing the Excel parts. This is the **knowledge mismatch** created by divergence in implementation patterns.

If you instead write a more permissive query that looks for either `ex:hasPart` or `leg:belongsTo` string matches, you might cobble together results, but that's brittle and error-prone.

Example leveraging the `OPTIONAL` SPARQL statement and (minimal) provenance to explicitly show:

```python
class PartOptionalComponents(PartComponents):
    sparql = """
    SELECT ?part ?partNumber ?source ?component WHERE {
        ?part a ex:Part ;
            ex:partNumber ?partNumber ;
            prov:wasDerivedFrom/rdfs:label ?source .

        # Find components that have the part (the authoritative GraphQL mapping)
        OPTIONAL {
            ?component a ex:Component ;
                ex:hasPart ?part .
        }
    }
    """

PartOptionalComponents.run_query(g1+g2)
```

| | part | partNumber | source | component |
|---|---|---|---|---|
| 0 | res:Part/PART-11 | FC-ACT-02 | RDBMS | res:Component/COMP-1 |
| 1 | res:Part/PART-10 | FC-SENSOR-01 | RDBMS | res:Component/COMP-1 |
| 2 | res:Part/FC-SENSOR-01 | FC-SENSOR-01 | CSV | None |
| 3 | res:Part/FC-GPS-01 | FC-GPS-01 | CSV | None |

### 4) Introduce SHACL to detect these data quality/structural mismatches

We now define SHACL shapes that specify how valid `ex:Component` and `ex:Part` instances should look.

> Note: the GraphQL mapping will satisfy these shapes; the Excel mapping will fail at least one

- `ComponentShape` that requires at least one `ex:hasPart` and that each `ex:hasPart` points to an `ex:Part`.
- `PartShape` (with example optional additional constraints)

```python
from IPython.core.magic import register_line_cell_magic
from pyshacl import validate

@register_line_cell_magic
def turtle(line, cell):
    G = Graph()
    return G.parse(data=cell, format="turtle")
```

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/ontology/> .
@prefix res: <http://example.org/resource/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:ComponentShape
  a sh:NodeShape ;
  sh:targetClass ex:Component ;
  sh:property [
    sh:path ex:hasPart ;
    sh:minCount 1 ;        # must have at least one part
    sh:class ex:Part ;     # values must be ex:Part instances
  ] .

ex:PartShape
  a sh:NodeShape ;
  sh:targetClass ex:Part ;
  sh:property [
    sh:path ex:partNumber ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] ;
  sh:property [
    sh:path ex:partType ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
  ] .
```

```python
conforms, results_graph, results_text = validate(
    data_graph=g1+g2,
    shacl_graph=shape_graphs,
    inference='rdfs',  # or 'none'
    abort_on_first=False,
    meta_shacl=False,
    debug=False,
)

print("Conforms:", conforms)
print(results_text)
```

```text
Conforms: True
Validation Report
Conforms: True
```

Why this does NOT catch the problem:

- The GraphQL/RDBMS mapping created `ex:Component` instances with `ex:hasPart` pointing to `ex:Part` instances, so it **passes** `ex:ComponentShape`.
- The Excel mapping does **not** create `ex:Component` URIs nor `ex:hasPart` triples. So **no `ex:Component` node from Excel exists** to validate as `ex:Component`; but the parts exist as `ex:Part` instances; however they are not linked via `ex:hasPart`. If you validate all nodes that *should* be Components, the expected `ex:Component` will appear only from GraphQL, and therefore pass validation.

More importantly, our target is to ensure *every part has a parent component* AND *every component has parts*, therefore the `ComponentShape` only reveals (implicitly) that some parts are not reachable via `ex:hasPart`.

To make this explicit (and cause a failure), we add an additional shape to assert that *every* `ex:Part` must be pointed to by some `ex:Component`: SHACL can't directly express inverse property with cardinality easily but you can require `ex:Part` to have a `leg:belongsTo` as `sh:property` with IRI pointing to `ex:Component`. The simplest approach is: add a `GraphConstraint` using `sh:SPARQL` to assert presence of a component that has the part.

Explicit Part Constraint:

```turtle
@prefix ex: <http://example.org/ontology/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

ex:PartHasParentConstraint
  a sh:NodeShape ;
  sh:targetClass ex:Part ;
  sh:sparql [
    a sh:SPARQLConstraint ;
    sh:message "Each Part must be linked from a Component via ex:hasPart" ;
    sh:select """
      SELECT $this
      WHERE {
        FILTER NOT EXISTS { ?comp a ex:Component ; ex:hasPart $this . }
      }
    """ ;
  ] .
```

Re-running validation with this shape added:

```text
Conforms: False
Validation Report
Conforms: False
Results (2):
Constraint Violation in SPARQLConstraintComponent:
    Severity: sh:Violation
    Source Shape: ex:PartHasParentConstraint
    Focus Node: <http://example.org/resource/Part/FC-SENSOR-01>
    Message: Each Part must be linked from a Component via ex:hasPart
Constraint Violation in SPARQLConstraintComponent:
    Severity: sh:Violation
    Source Shape: ex:PartHasParentConstraint
    Focus Node: <http://example.org/resource/Part/FC-GPS-01>
    Message: Each Part must be linked from a Component via ex:hasPart
```

Why this catches the problem: when you run a SHACL validator (e.g., `pySHACL`) on the merged graph with these shapes:

- `ex:Part/PART-10` and `PART-11` pass `ex:PartHasParentConstraint` because there exists a component with `ex:hasPart` pointing to them.
- `res:Part/FC-SENSOR-01` and `res:Part/FC-GPS-01` fail the constraint since no `ex:Component` has `ex:hasPart` pointing to them.

### 5) Fix / align the Excel mapping to SHACL and the ontology

There are two realistic alignments for this situation:

**A.** Create `ex:Component` URIs from the Excel sheet, normalize component names to canonical IDs (e.g., use a mapping or normalization function that maps `"Flight Control"` and `"FlightControl"` to `COMP-1` or to a canonical name). Then link parts to the component with `ex:hasPart`. Example: look up component by name or call fuzzy matching and then add the `ex:hasPart res:Part/FC-SENSOR-01` triple.

**B.** Add `owl:sameAs` / `skos:exactMatch` statements between Excel component URIs and GraphQL component URIs (if both sides produced component URIs but with different patterns). Or declare `leg:belongsTo` as `rdfs:subPropertyOf ex:hasPart` **if** the legacy property points to the resource (not a literal).

> Note: there is quite a bit of discussion concerning the downsides to using `owl:sameAs` for non-ontology entities, so I tend to avoid it where possible.

Let's show **A**: normalize and create `ex:Component` URIs and `ex:hasPart` triples in the Excel mapping process.

```python
import csv
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

EX = Namespace("http://example.org/ontology/")
RES = Namespace("http://example.org/resource/")
LEG = Namespace("http://example.org/legacy/")

g2 = Graph()
g2.bind("ex", EX)
g2.bind("res", RES)
g2.bind("leg", LEG)

# Suppose we have a canonical name mapping (maybe via a lookup or fuzzy match)
canonical_component_map = {
    "flightcontrol": URIRef(f"{RES}Component/COMP-1"),
    "flight control": URIRef(f"{RES}Component/COMP-1"),
    "flight_control": URIRef(f"{RES}Component/COMP-1"),
}

with open("legacy_parts.csv", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        comp_name = row['component_name'].strip()
        pnum = row['pnum'].strip()
        ptype = row['type'].strip()
        # normalization: lower-case, remove spaces/underscores
        key = comp_name.lower().replace(" ", "").replace("_", "")
        # simpler: map by known lower-case forms
        comp_uri = canonical_component_map.get(comp_name.lower(), None)
        if comp_uri is None:
            # fallback: generate a normalized URI
            comp_uri = URIRef(f"{RES}Component/COMP-{comp_name.replace(' ','_')}")
        # Create component resource if not exists
        g2.add((comp_uri, RDF.type, EX.Component))
        # Create part URI consistent with GraphQL style: PART-<id> is not available here;
        # We can still use pnum-based URI but link from component via ex:hasPart
        part_uri = URIRef(f"{RES}Part/{pnum}")
        g2.add((part_uri, RDF.type, EX.Part))
        g2.add((part_uri, EX.partNumber, Literal(pnum)))
        g2.add((part_uri, EX.partType, Literal(ptype)))
        # Now link properly
        g2.add((comp_uri, EX.hasPart, part_uri))
        # part provenance
        csv_bnode = BNode()
        g2.add((part_uri, RDF.type, PROV.Entity))
        g2.add((part_uri, PROV.wasDerivedFrom, csv_bnode))  # placeholder
        g2.add((csv_bnode, RDFS.label, Literal("CSV")))

# Serialize to turtle
print(g2.serialize(format="turtle"))
```

```turtle
@prefix ex: <http://example.org/ontology/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/resource/Component/COMP-1> a ex:Component ;
    ex:hasPart <http://example.org/resource/Part/FC-GPS-01>,
        <http://example.org/resource/Part/FC-SENSOR-01> .

<http://example.org/resource/Part/FC-GPS-01> a ex:Part,
        prov:Entity ;
    ex:partNumber "FC-GPS-01" ;
    ex:partType "Sensor" ;
    prov:wasDerivedFrom [ rdfs:label "CSV" ] .

<http://example.org/resource/Part/FC-SENSOR-01> a ex:Part,
        prov:Entity ;
    ex:partNumber "FC-SENSOR-01" ;
    ex:partType "Sens" ;
    prov:wasDerivedFrom [ rdfs:label "CSV" ] .
```

After this alignment:

- `res:Component/COMP-1 ex:hasPart res:Part/FC-SENSOR-01` exists.
- SHACL validation now passes for those parts (the SPARQL parent test is satisfied).
- The earlier SPARQL query that searched for `?component ex:hasPart ?part` will now return the newly aligned Excel parts as well.

| | part | partNumber | source | component |
|---|---|---|---|---|
| 0 | res:Part/PART-11 | FC-ACT-02 | RDBMS | res:Component/COMP-1 |
| 1 | res:Part/PART-10 | FC-SENSOR-01 | RDBMS | res:Component/COMP-1 |
| 2 | res:Part/FC-SENSOR-01 | FC-SENSOR-01 | CSV | res:Component/COMP-1 |
| 3 | res:Part/FC-GPS-01 | FC-GPS-01 | CSV | res:Component/COMP-1 |

Thus, the *missing knowledge* identified previously is now integrated and discoverable.

### Summary: Why OWL+SHACL coupling is helpful here

- **OWL** is great for conceptual modeling and for allowing reasoning (class hierarchies, equivalences), but it **does not** express application-level structural constraints like "every component must have at least one part" in a way that produces concrete validation reports for data producers.
- **SHACL** expresses constraints and *validates* instance data against them. In our example: the GraphQL mapping produced RDF that satisfied the SHACL shapes (so it looked "good"); the Excel mapping produced RDF that omitted required structural links (or used different properties), which SHACL uncovered as validation failures.
- SHACL therefore helps discover the **implementation pattern mismatch** (different URI schemes, missing relationships, legacy properties used incorrectly) that OWL alone wouldn't flag as an error; OWL doesn't require `ex:hasPart` conjoints, nor does it flag missing links as validation errors.
- Once the Excel data is aligned (either by normalizing IDs, adding `ex:hasPart`, or adding `owl:sameAs`), the SHACL shapes will be satisfied and queries will return the complete integrated knowledge.

### Practical notes / recommendations for real MBSE projects

- **Agree on canonical identifier patterns** (URIs) early: teams exposing GraphQL and legacy Excel should use a shared ID policy or a mapping registry.
- **Add an ingestion step** that runs SHACL validation on incoming datasets and produces human-understandable reports for data owners; that lets you fix mappings before merging into the triplestore.
- **Use a reconciliation / entity resolution step** when ingesting looser data sources (Excel, CSV), to create canonical URIs (or mappings e.g. `skos:exactMatch` / `skos:closeMatch`).
- Consider declaring legacy properties as subProperties of canonical properties (e.g., `leg:belongsTo rdfs:subPropertyOf ex:hasPart`) only if they have compatible semantics and point to the same kinds of objects (not literal names). This sometimes helps, but requires careful governance.
- Automate the alignment (normalization functions, fuzzy matching, lookup tables) and re-run SHACL until graphs conform.

## Downsides and Challenges to a "Federated Services" Approach

### 1. Integration Cost Is Deferred, Not Eliminated

| Aspect | What Happens | Consequence |
|---|---|---|
| Incremental mapping | Each domain publishes RDF and adds SHACL gradually. | The sum of many local efforts can exceed the cost of one large, up-front ontology project. |
| Long tail of partial conformance | Different groups align at different rates. | Persistent semantic mismatches ("semantic debt") accumulate. |
| Discovery lag | Relationships among systems may only emerge after data is validated and reasoned over. | Cross-domain queries can be incomplete until sufficient mappings exist. |

> Trade-off: The work becomes more distributed and iterative, but less predictable and coordinated.

### 2. Governance and Coordination Overhead

- Distributed ownership means each team controls its shapes and mappings. Without strong stewardship, you get divergent URI patterns, vocabularies, and versioning; inconsistent application of ontology patterns (`ex:hasPart` vs `ex:partOf`); and competing local ontologies that make reasoning brittle.
- Ontology drift occurs when local teams extend or fork the core ontology faster than governance can review it.
- Requires a meta-governance layer (often a "shape registry" or "vocabulary service") just to track who uses what predicates and shapes.

> Net: You trade one central choke-point (a monolithic ontology committee) for many small friction points.

### 3. Tooling Maturity and Developer Friction

- RDF/SHACL tooling still lags far behind mainstream developer ecosystems: limited IDE support, schema introspection, debugging UX.
- Poor native support in data engineering stacks (Spark, dbt, Airflow, etc.).
- SHACL validation at scale is computationally expensive; naive implementations don't parallelize well.
- SPARQL federation across large distributed graphs is complex to optimize and cache.

> Enterprises often end up building custom orchestration or caching layers; costly engineering work just to achieve performance parity with SQL or API federation.

### 4. Knowledge Graph Modeling Overhead

- Each system must learn enough about RDF modeling, namespaces, and IRIs to publish useful triples.
- The mapping layer (e.g., R2RML, CSV-to-RDF, JSON-LD contexts) becomes a specialized skill set.
- Debugging semantic errors is harder than debugging syntactic ones; e.g., the data "looks fine" but reasoning produces empty results because classes or predicates are misaligned.
- The cognitive load is high; non-ontologists can be alienated, slowing adoption.

### 5. Delayed Business Value

Ontology-first efforts fail because they over-design early; RDF + SHACL efforts risk under-delivering early. Early stages often produce minimal reasoning value (because graphs are thin and only partially linked), repeated validation cycles that don't yet feed real applications, and stakeholder frustration ("why is this taking so long to show ROI?").

> You need visible integration exemplars or "lighthouse projects" to justify the ongoing investment.

### 6. Reasoning and Query Complexity

- Open-world reasoning introduces ambiguity: absence of a triple ≠ falsity, which makes "must have" constraints hard to express beyond SHACL.
- Inference explosion: even modest OWL reasoning can balloon data size and query time.
- Federated inference (reasoning over multiple partial graphs) is still immature.

> Enterprises often need hybrid architectures: use reasoning for metadata and discovery, not for every transactional query.

### 7. Weaknesses Compared to an Ontology-First Approach

| Area | Ontology-First Strength | Federated RDF + SHACL Weakness |
|---|---|---|
| Conceptual coherence | Enterprise starts with one conceptual model; easier to communicate strategy. | Ontology evolves piecemeal; shared semantics emerge later. |
| Predictability | Clear data contracts from day one. | Early integrations are ad-hoc, partial, sometimes inconsistent. |
| Compliance & audit | Easier to certify one ontology for regulatory or safety cases. | Harder to prove enterprise-wide conformance when semantics are distributed. |
| Change management | Central change control simplifies versioning. | Version proliferation; multiple SHACL shape versions across teams. |
| Performance tuning | Centralized model allows uniform optimization. | Federated reasoning and query optimization are harder. |

In short: federated models maximize agility but weaken guarantees.

### 8. Sociotechnical and Cultural Challenges

- **Ontology expertise bottleneck:** Each domain team needs at least one semantic engineer.
- **Mindset gap:** Traditional DBAs and API developers think in schemas, not triples or shapes.
- **Governance fatigue:** Continuous alignment conversations can feel endless without strong facilitation.

> Culture often determines success more than technology; without buy-in, teams revert to CSVs and REST APIs.

### 9. Security and Access Control

RDF's open graph model complicates row-level and attribute-level security:

- Federation may inadvertently expose sensitive triples if ACLs aren't enforced per graph.
- Standard SPARQL lacks enterprise-grade fine-grained authorization.
- Ontology-first systems often centralize security and can enforce policy more uniformly.

### 10. Summary Table: The Core Trade-off

| Dimension | Federated RDF + SHACL | Ontology-First |
|---|---|---|
| Agility | High | Low |
| Governance Complexity | Distributed | Centralized |
| Conceptual Coherence | Emergent | Designed |
| Time to Partial Value | Fast | Slow |
| Time to Enterprise Coherence | Long | Moderate (if successful) |
| Tooling & Skill Requirements | Specialized, fragmented | Concentrated upfront |
| Risk Profile | Operational fragmentation | Bureaucratic stagnation |

### 11. Takeaway

A federated RDF + SHACL strategy is best when:

- You have many semi-autonomous data producers.
- The cost of semantic divergence is acceptable in the short term.
- You can invest in progressive alignment infrastructure (shape validation pipelines, ontology registry, data catalog).

It becomes risky when:

- The enterprise demands strict, auditable semantic consistency (e.g., regulated industries).
- Governance capacity is weak or under-resourced.
- Leadership expects fast, uniform integration outcomes rather than gradual harmonization.
