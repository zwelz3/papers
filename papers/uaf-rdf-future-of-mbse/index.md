*UAF shapes how we build systems. RDF ensures those systems can understand each other. Together, they may define the future of Model-Based Systems Engineering.*

## Motivating the Discussion: UAF? RDF? Why?

The Unified Architecture Framework (UAF) provides a standardized way to model complex systems and their relationships across operational, capability, and technical viewpoints. It helps ensure that Model-Based Systems Engineering (MBSE) efforts produce consistent, traceable, and high-quality architectures that align with organizational and mission objectives.

The Resource Description Framework (RDF), by contrast, is a formal web standard for representing and linking data in a machine-interpretable way. RDF technologies encompass standards for graph specification, query, and validation. These technologies enable systems models, data, and tools to share meaning across organizational and technological boundaries, supporting the (long sought-after) digital engineering goals of integration and interoperability.

Together, UAF and RDF provide an opportunity to bridge the gap between well-structured model creation and semantic data exchange, helping to ensure that future MBSE products are both rigorous in their internal structure and connected across the broader digital ecosystem.

## Background on UAF

UAF is currently managed by the Object Modeling Group (OMG), an international non-profit consortium-led standards organization. From the [UAF 1.2 Specification](https://www.omg.org/spec/UAF/1.2/):

> *UAF is an OMG standard that assists in development of architectural descriptions in commercial industry firms, federal government agencies and defense organizations. UAF has a variety of use cases from Enterprise and Mission architecting, to System of Systems (SoS) and Cyber-physical Systems engineering, as well as being an enabler for Digital Transformation efforts and for Department of Defense Architecture Framework (DoDAF) and NATO Architecture Framework (NAF) modeling.*

The UAF spec is split into two parts: the Domain Meta-Model (DMM), and the UAF Modeling Language (UAF ML). UAF ML specifies the implementation of the UAF DMM in terms of the Unified Modeling Language (UML) and Systems Modeling Language (SysML). It prescribes UML extensions that describe the UAF DMM, and is also dependent on a SysML (v1) profile (itself an extension to UML).

UAF has unified existing architecture frameworks such as DoDAF (US), MODAF (UK), and NAF (NATO), and is being actively developed and improved. Each of these frameworks have evolved from a common foundation captured in the International Defence Enterprise Architecture Specification (IDEAS) ontology. The difference between the foundational IDEAS ontology (with relation to the Business Objects Reference Ontology, aka BORO) and modern *semantic* ontologies will be discussed later in this discussion. I highly recommend the interested reader check out [this conference paper](https://www.researchgate.net/publication/335222111_Foundational_Choices_in_Enterprise_Architecture_The_Case_of_Capability_in_Defense_Frameworks) that discusses the original design principles (and limitations) of UAF/DoDAF/MODAF.

## Background on RDF (and RDF Technologies)

The Resource Description Framework (RDF) originated from the early vision of the Semantic Web, which sought to make data on the internet machine-readable and linked through shared meaning. RDF represents information as simple subject–predicate–object triples, allowing knowledge to be expressed as interconnected graphs rather than isolated documents. Individual terms for concepts (e.g. “Vehicle”), instances (e.g. “*this specific* Vehicle”) and relationships (predicates, e.g. “has owner”) are represented using Uniform Resource Identifiers (URIs), which leverage internet protocols to uniquely identify a resource so that, when dereferenced, it can be accessed or resolved to meaningful information about that entity.

Building on this foundation, standard RDF technologies such as SPARQL (for querying graph data) and SHACL (for defining and validating data constraints) emerged to make RDF both powerful and practical for enterprise use. Together, these tools enable organizations to integrate, validate, and reason over diverse datasets while maintaining semantic consistency.

Over time, RDF has evolved beyond academic web research into a backbone for knowledge graphs that power modern industries like FinTech, Healthcare, and Advertising and companies like Palantir, Google, and AstraZeneca. RDF supports data exchange, compliance, and analytics across distributed systems at scale, turning once-siloed information into interoperable, queryable, and trustworthy knowledge assets.

## On the Compatibility of UAF and RDF for MBSE

While UAF and RDF technologies may both support the future of MBSE and digital engineering, their compatibility is not implicit and requires unpacking to understand how these might work together.

### UAFML’s Roots: MOF, UML, and Closed-World Assumptions

The metamodel-based worldview, which includes UAF, SysML, and UML, is *prescriptive*. It is built upon the OMG’s 4-level Meta-Object Facility (MOF) architecture. This architecture is strictly layered: M3 (the meta-metamodel, MOF itself), M2 (the metamodel, e.g., the UAF Domain Meta-Model), M1 (the user's model, e.g., a specific Car architecture), and M0 (the instances of that model, e.g., Thing_Number_001). The defining characteristic is the *strict separation* of these meta-layers, i.e. an element at M1 must be a valid instance of a class at M2. This rigid, top-down structure provides structural validation and enforced correctness, which is the primary goal of model management and visualization. This worldview is designed to help engineers build a correct and complete model of a single, bounded system.

UAFML (Unified Architecture Framework Modeling Language) inherits its foundations from the UML metamodel, standardized through MOF. This means that it relies on class-instance relationships defined structurally (e.g., by containment and strict typing) rather than semantically (by property assertions), and uses diagrams, typed associations, and multiplicities that have precise behavioral semantics (*locally*, within a model). UAFML assumes a *closed-world model* (closed world assumption, CWA), meaning that if something isn’t modeled it is false, or does not exist.

RDF, by contrast is declarative and makes the *open-world assumption* (OWA) (by default), which means that there is no rigid set of layers to the RDF stack and the absence of a statement doesn’t make it false, but rather “unknown.” RDF is triplet-based, not object-based; everything is expressed as subject–predicate–object, without an inherent containment or schema enforcement (although named graphs, ontologies and/or SHACL change this behavior). RDF treats “type” (rdf:type) as just another property within the framework, i.e. it is semantically extensible, but not structurally enforced (again, by default).

This creates a fundamental mismatch between the “metamodel” (i.e. MOF) and “semantic” (i.e. ontological) paradigms.

### Metamodel vs Semantic/Ontology Paradigm

UAFML’s metamodel (and its underlying IDEAS foundation) is ontologically *inspired*, but it is not an ontology in the RDF technology, i.e. Web Ontology Language (OWL), sense. The following table captures some differences between aspects of the two.

| Aspect | UAFML (MOF-based) | RDF Technologies |
|---|---|---|
| Primary Goal | Model correctness & visualization | Data federation, integration & reasoning |
| World Assumption | Closed world: if not modeled, it's false | Open world: if not stated, it's unknown |
| Primary Representation | Classes, attributes, associations, and slots | Triples (subject--predicate--object) |
| Semantics | Defined by the modeling language (UML semantics) | Defined by model theory (RDF semantics) |
| Constraint Language | OCL / MOF constraints | SHACL / OWL axioms |
| Identity | GUIDs or model element references | URIs (global identifiers) |
| Extensibility | Limited, via stereotypes and profiles | Unlimited, via new vocabularies and linked ontologies |

If you were to try and express a UAF model in RDF, you would face a *flattening problem*. UAF’s “meta-meta” structure (element - classifier - metaclass) doesn’t map cleanly to RDF’s single-level predicate graph without losing key semantics like inheritance scope, diagram context, or constraint validation. This is primarily the result of the implicit semantics of UAF ML that would require additional specification to support RDF’s explicit semantics.

The technical divide detailed in the table is not merely a matter of implementation choice; it is the practical manifestation of a deeper, philosophical divergence between two professional communities. The UAF/MBSE community is rooted in systems and software engineering and is concerned with building a new “correct” thing. For this "builder" culture, the rigid and prescriptive CWA-based metamodel is necessary; it provides the guardrails to ensure a design is complete, consistent, and valid against its specification. 

The RDF/Semantic Web community, rooted in information science and web architecture, is concerned with integrating existing, diverse information. For this "integrator" culture, a rigid, prescriptive metamodel is a *barrier*. The OWA, flexible schemas, and declarative semantics are necessary to merge disparate datasets without causing schema conflicts or requiring a single, monolithic, top-down authority. The current friction in MBSE, particularly in its "digital thread" aspirations, stems from the novel requirement that these two cultures, and their respective technologies, must now interoperate. 

### A Note on the IDEAS Ontology vs RDF (i.e. OWL) Ontologies

While the IDEAS ontology at the foundation of UAF *looks* like an ontology, it’s not implemented in RDF/OWL (or defined using explicit semantics). IDEAS is a *conceptual* ontology (no pun intended) that is defined in a first-order logic (FOL) framework.

In IDEAS, individuals have temporal parts, e.g., whole-lifetime identity, whereas RDF does not natively support 4D temporal parts; it requires custom vocabularies/ontologies i.e. the Common Core Ontologies (CCO) Time Ontology. IDEAS utilizes *extensional identity,* meaning that an individual is defined by its spatiotemporal extent; for UAF 1.2 this means that in order to make assumptions about class equivalence, one compares its properties in time for equivalence. In contrast, the explicit semantics of RDF are non-extensional by default, meaning that one cannot guarantee that two subjects (URIs) with identical properties are identical individuals. This means that while UAF is particularly well-suited to managing relationships between models such as “reference architectures” or system “meta-models”, it is less suited to disambiguating between instantiations of these models (i.e. real-world instances of a system/part/etc.). In contrast, RDF is designed in such a way that instances with identical properties yet unique URIs (i.e. two identical simulation configuration files) cannot be resolved to a common entity via inference. Instead, one must apply additional processes (i.e. graph embedding comparisons) to make assumptions about equivalence (note: this is by design and not a consequence of RDF).

Therefore, the implicit formal underpinnings of IDEAS (which UAF depends on for “truth conditions”) do not exist (by default) in RDF’s logical model.

### Tooling and Exchange (Model/Vendor Lock-In)

While UAF as a framework is tool-agnostic, UAF ML is designed for MBSE tools like MagicDraw/Cameo, which depend on XMI (XML Metadata Interchange) for serialization (up to UAF v1.2, although this may change with UAF v2). This introduces friction because identifiers are tool-local (not URI-based i.e. globally resolvable), relationships are navigable references but not semantically addressable, and diagrammatic context (views, layers, partitions) is integral to meaning (or rather *interpretation)*.

As a result, even though you can export UAF concepts into RDF (say, by mapping UAF elements to RDF classes and relationships to properties), the implicit semantics that make UAF “UAF” (e.g. architectural view consistency, meta-layer validation, and strict typing) cannot be enforced or queried naturally in an RDF store; at least, not without further extension to UAF.

These limitations cause a heavy reliance on the specific implementations of individual tools/vendors, and makes the reuse, sharing, and utilization of MBSE models/tools a challenge. This has been a common complaint for adopters of UAF v1.2 and SysML v1, and has been a driving force for the development of SysML v2 (which I will leave for a future article), future extension of UAF (as part of v2 development), and the rise in utilization of RDF technologies for MBSE information exchange (i.e. the INCOSE Digital Engineering Information Exchange Ontology).

## Summarizing Current Incompatibility and Identifying Opportunities

The design gap between UAF/UAF ML and RDF technologies can be summarized in the table:

| Category         | UAF/UAFML (MOF-based)              | RDF Technologies                    |
|------------------|------------------------------------|-------------------------------------|
| World Assumption | Closed                             | Open                                |
| Identity         | Local, tool-scoped                 | Global, URI-based                   |
| Semantics        | Procedural / diagrammatic          | Declarative / logical               |
| Relations        | n-ary, typed associations          | binary predicates (w/o reification) |
| Validation       | MOF/OCL rules                      | SHACL/OWL inference                 |
| Purpose          | Model management and visualization | Semantic integration and reasoning  |

Because the current implementation of UAF ML requires the CWA, strongly typed, meta-layered modeling paradigms to function properly, it loses much of its integrity and usefulness when a rich, multi-layered, procedural metamodel is "flattened" into a single-layer, declarative RDF graph. The problem is compounded with more complex UAF constructs. UAF models are full of "Exchanges" e.g., an InformationExchange between two OperationalPerformers. This Exchange is an *association* that has its own attributes (e.g., payload, timing, frequency); this is an n-ary relationship, as it relates three or more things: Performer1, Performer2, and the Payload. RDF triples, by definition, are strictly binary (subject-predicate-object). To model an n-ary relationship, RDF must *reify* the statement. As shown in the RDF specification and the newer RDF-Star standard, to reify one must create a new resource (e.g., ex:Exchange_001) to represent the relationship itself, and then attach properties to it. 

Perhaps the most significant loss is that of *implicit context*; the core value proposition of UAF is its Viewpoints (e.g., Operational, Strategic, Resources, Personnel) and the Views (diagrams) that represent them. The precise meaning of an element in UAF is often implicitly determined by which diagram (e.g., OV-2, SV-1) it appears in. Ensuring "cross-view consistency" and adhering to "View Specifications" is a primary challenge for UAF modelers. To capture this context within RDF would require a significant amount of additional descriptive logic (i.e. ontologically-scoped named graphs, complex reification, or extensive nth-degree relationship chains).

That said, there are situations where the utility of integrating these frameworks can be useful for the advancement of MBSE. Below are some opportunities for a combined approach:

- Export selected UAF views (e.g., Operational Viewpoint) into RDF for interoperability

- Use RDF technologies to federate cross-domain data linked to specific UAF artifacts

- Determine a process to utilize SHACL shapes to approximate UAF constraints

- Mappings (i.e. UML to RDF) can provide value at the “information exchange” layer

This indicates that there is an area of integration that may prove beneficial: using UAF for model/architecture structure, and using RDF technologies for semantic meaning, information exchange, and integration across data, tools, and models.

## Conclusion

UAF and RDF represent two complementary pillars of digital engineering. One focuses on creating precise, high-quality system architectures, and the other on connecting those architectures within a broader semantic ecosystem. As the MBSE landscape evolves, integrating model-based rigor with graph-based semantics will likely be key to realizing the promise of a truly interoperable digital thread. By aligning UAF’s structured modeling discipline with RDF’s open, web-native data exchange, organizations can begin to unify engineering intent and digital knowledge across domains, tools, and lifecycles.

The purpose of this article was to present a high-level, yet technically accurate, diagnosis of a fundamental challenge in digital engineering; that the historical challenge of developing highly-specific system models is in conflict with the modern goals of interoperability, integration, and the idea of the “digital thread.” Hopefully this discussion has enforced the idea that UAF's structured, model-based rigor and RDF's open, graph-based semantics are both essential but inherently incompatible in their current (UAF 1.2) implementations. As a result, organizations should treat existing UAF 1.2 models as *legacy data silos* that either require “semantic wrappers” capable of mapping information to a form more readily integrated, or future alignment with the emerging SysML v2 standard (and its alignment with RDF/OWL).

In a future extension to this discussion, I will explore the utilization of specific RDF technologies with SysML v2 in support of an Open Digital Thread to serve the DoD Mission Engineering, Digital Engineering, and MBSE communities.
