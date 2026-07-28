*Traditional Model-Based Systems Engineering (MBSE), anchored to domain-specific modeling languages such as SysML, has long been positioned as the path toward rigorous, tool-supported systems design. The latest iteration, SysML v2, attempts to address well-known shortcomings by introducing a textual syntax amenable to version control and automation; an approach commonly described as "models as code." This paper argues that this evolution, while directionally sound, does not go far enough and may be too late. Three converging developments undermine the need for a purpose-built modeling language: (1) general-purpose programming languages can express system models with superior tooling and ecosystem support; (2) large language models (LLMs) can now generate, translate, and validate between natural language, code, tests, and diagrams in an idempotent, version-controlled manner; and (3) mature semantic web technologies (RDF, OWL, SHACL) provide domain-independent ontological and inferential capabilities that subsume SysML's claim to shared semantics. Together, these developments suggest a "code as models" paradigm that renders the traditional MBSE toolchain redundant for most practical purposes.*

## 1. Introduction: The Promise and Pain of MBSE

Model-Based Systems Engineering emerged as a response to document-centric engineering processes that struggled to maintain consistency across complex system designs. The central promise was compelling: a single, authoritative model would serve as the source of truth for system structure, behavior, requirements, and verification; replacing fragmented documents with a connected, analyzable representation.

In practice, this promise has been only partially realized. SysML v1 models are typically stored in opaque, vendor-specific formats. Interoperability between tools remains largely fictional despite standardization efforts. The cost of tooling is high, the learning curve steep, and the gap between "the model" and "the actual system" persistent. Models frequently become stale artifacts maintained by specialists rather than living engineering documents that drive decisions.

SysML v2, currently undergoing standardization by the Object Management Group (OMG), attempts to address several of these problems. Its most significant departure is the introduction of a textual concrete syntax designed to be the primary authoring format. This enables version control, diffing, and merge workflows familiar to software engineers. The approach has been described as "models as code," borrowing the legitimacy of software engineering practices to shore up MBSE's credibility.

This paper examines whether "models as code" goes far enough, or whether the entire premise of a purpose-built modeling language is now being overtaken by broader technological shifts.

## 2. The 'Models as Code' Argument and Its Limitations

The "models as code" argument for SysML v2 rests on several pillars. First, textual models can be managed in standard version control systems (Git), enabling distributed collaboration, branching, pull requests, and code review. Second, text-based models can be processed by CI/CD pipelines for automated validation, transformation, and artifact generation. Third, a standardized textual format breaks vendor lock-in, allowing any conformant tool to parse and manipulate the model.

These are genuine improvements over SysML v1's diagram-centric, tool-locked paradigm. However, the approach carries inherent limitations that its advocates tend to understate.

SysML v2 remains a domain-specific language with a small ecosystem. IDE support, linter quality, debugging tools, and library availability are orders of magnitude behind general-purpose languages like Python, TypeScript, or Rust. The textual syntax must still be learned by systems engineers who are, by training and inclination, not software developers. The OMG standardization process introduces a pace of evolution measured in years or decades, while the problems MBSE addresses evolve at the pace of engineering programs.

Most critically, "models as code" still assumes that a dedicated modeling language is the correct level of abstraction. It moves the representation from diagrams to text, but it does not question whether the representation itself is necessary; or whether the same objectives could be achieved by expressing system models directly in general-purpose code.

## 3. Code as Models: The Inverted Paradigm

The alternative paradigm, which we term "code as models," inverts the traditional MBSE assumption. Rather than creating a specialized language to represent system models, it uses general-purpose programming languages as the modeling medium. System structure, behavior, constraints, and interfaces are expressed as typed data structures, executable logic, and automated tests.

This approach offers several concrete advantages. System architecture can be defined as typed data structures in Python or TypeScript, inheriting mature IDE support, static analysis, type checking, and a vast ecosystem of libraries. Constraints and validation rules become executable tests (using frameworks such as pytest or property-based testing) rather than OCL expressions or SysML constraint blocks. Diagrams (using tools like Mermaid, PlantUML, D2, or Graphviz) become derived views rendered from the code, not the source of truth. Version control, CI/CD integration, and collaborative workflows come naturally because the artifacts are already native to the software development ecosystem.

The historical objection to this approach has been that systems engineers cannot code. This objection is increasingly moot; not because systems engineers have suddenly learned to program, but because large language models have fundamentally changed the relationship between human intent and code generation.

## 4. LLMs as the Translation Layer

Large language models represent a qualitative shift in the feasibility of the "code as models" paradigm. Modern LLMs can fluently translate between natural language descriptions of system architecture and formal code representations. They can generate data structures from prose requirements, produce test suites from constraint specifications, render diagrams from structural descriptions, and refactor models across representations.

Critically, this translation is increasingly idempotent and deterministic when managed within version-controlled codebases. An LLM can regenerate a diagram from an updated model, revalidate constraints after a design change, or translate a subsystem interface specification into an integration test; all within a standard Git workflow. The output is diffable, reviewable, and auditable.

This capability dissolves the primary rationale for a domain-specific modeling language. The DSL existed because there was a gap between how engineers think about systems and how formal representations are authored. LLMs close that gap by serving as a universal adapter between human-scale reasoning and machine-processable code. The modeling language was a bridge; the bridge is no longer needed when the river can be crossed directly.

Furthermore, LLMs can operate across representation boundaries in ways that a single modeling language cannot. The same LLM that generates a Python system model can produce a verification plan, draft interface control documents, generate simulation harnesses, and create stakeholder-facing presentations; all from the same underlying codebase. SysML, by design, addresses only the modeling layer.

## 5. Semantic Web Technologies as the Ontological Foundation

The remaining argument for SysML v2 (i.e. KerML) centers on shared semantics: the idea that a common modeling language provides a standardized vocabulary for systems engineering concepts (parts, ports, connections, requirements, allocations) enabling tool interoperability and cross-organizational communication.

This argument is undermined by the maturation and demonstrated effectiveness of semantic web technologies; specifically, OWL (Web Ontology Language), and SHACL (Shapes Constraint Language) as RDF technologies. These provide a general-purpose, standards-based framework for exactly the problem SysML claims to solve, but without the limitation of being confined to a single domain (and of limited value at the time of writing i.e. SysML v2.0).

OWL ontologies can express the same structural concepts that SysML defines as language keywords: part-whole decomposition, port-based interfaces, requirement-satisfaction relationships, and allocation mappings. But unlike SysML's metamodel, which bakes domain semantics into language syntax, OWL ontologies treat semantics as data. They can be versioned, extended, composed with ontologies from adjacent domains, and reasoned over; all without modifying a language grammar or waiting for an OMG revision cycle.

SHACL provides structural constraint validation analogous to SysML v2's constraint blocks, but decoupled from any specific authoring environment. Shapes are defined against RDF graphs; the data can originate from any source (code-generated, manually authored, extracted from legacy documents by LLMs, or imported from suppliers). This is a fundamentally more flexible architecture than one that couples validation to a modeling language's type system.

The inferential capabilities of OWL add a dimension that SysML has no equivalent for. Deriving implicit relationships, checking consistency across a knowledge graph, and querying across federated datasets from multiple organizations are capabilities native to the semantic web stack. MBSE toolchains have historically treated these as aspirational features; in the RDF ecosystem, they are operational.

Perhaps most significantly, RDF-based ontologies are domain-independent. The same ontological infrastructure that represents system architecture can be extended to encompass manufacturing processes, supply chain logistics, operational environments, regulatory compliance frameworks, failure mode taxonomies, and maintenance procedures. SysML's metamodel is a walled garden; RDF-based ontologies form a web.

## 6. The Dissolution of MBSE as a Distinct Discipline

The convergence of these three developments (general-purpose code as the modeling medium, LLMs as the translation layer, and semantic web technologies as the ontological foundation) has an uncomfortable implication for the MBSE community: it dissolves MBSE as a distinct technical discipline.

What remains is a decomposition into existing, more mature fields. Executable behavior and automation belong to software engineering. Ontology, shared semantics, and inferential reasoning belong to knowledge engineering. The intellectual work of system decomposition, integration analysis, and trade-off evaluation belongs to systems thinking; which is a cognitive discipline, not a tool feature.

There is no layer in this decomposition where "and therefore you need SysML" is a necessary conclusion. The modeling language becomes an unnecessary intermediary between the engineer's intent and the formal representations that actually perform the analytical and integrative work.

This is not to say that the problems MBSE addresses are unimportant. They are critical. Complex systems require rigorous approaches to architecture, requirements traceability, interface management, and verification planning. The argument is that these problems are better solved by composing general-purpose technologies than by investing in a purpose-built ecosystem with a limited user base, slow evolution, and high adoption friction.

## 7. The Institutional Counterargument

The strongest remaining case for traditional MBSE and SysML is institutional, not technical. Large defense and aerospace programs have spent decades building processes, training curricula, contract data requirements lists (CDRLs), and organizational structures around MBSE. The U.S. Department of Defense Digital Engineering Strategy references MBSE explicitly. Standards bodies such as INCOSE have MBSE at the center of their vision for the future of systems engineering.

These institutional investments are real, and the cost of changing them is substantial. A large program that has mandated SysML deliverables in its contracts cannot easily pivot to "give us a Git repository with Python models and an OWL ontology."

However, institutional arguments are inherently conservative; they explain why change is slow, not why it should not occur. The history of engineering is replete with examples of incumbent methodologies persisting for years after technically superior alternatives emerged, sustained by contractual inertia and organizational risk aversion. The question is not whether the transition will happen, but how long it will take and what the catalyst will be.

A plausible catalyst would be a visible, high-profile program that demonstrates the "code as models" approach delivering superior results: better traceability, faster iteration, more effective cross-domain integration, and lower tooling costs. If such a demonstration is coupled with an opinionated, easy-to-adopt open-source framework (analogous to what Ruby on Rails did for web development), the institutional consensus could shift more rapidly than the current MBSE establishment expects.

## 8. Conclusion

SysML v2's "models as code" approach represents a genuine improvement over the diagram-centric, vendor-locked paradigm of SysML v1. But it is an incremental evolution within a framework whose foundational assumptions are being overtaken by broader technological developments.

The combination of general-purpose programming languages, large language models, and semantic web technologies provides a more capable, more flexible, and more economically sustainable alternative to purpose-built modeling languages. This "code as models" paradigm does not merely replicate what MBSE does in a different syntax; it subsumes it, while simultaneously enabling cross-domain integration that SysML was never designed to address.

The systems engineering community should recognize that the value of MBSE lies in the discipline of rigorous, model-based thinking about complex systems; not in any particular language or toolchain. That discipline is better served by tools that meet engineers where they are, leverage the massive investment in software engineering infrastructure, and evolve at the pace of the broader technology landscape rather than the pace of standards committees.

The models-as-code bridge was a step in the right direction. But the destination was always the other shore: code as models, augmented by AI and grounded in open, composable ontologies.
