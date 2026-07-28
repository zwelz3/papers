*Digital engineering is usually marketed as model-based engineering. I think its endgame is model-generated engineering: a semantic model held as the authoritative engineering asset, with the documents, matrices, diagrams, and review packages we currently maintain by hand produced as generated, provenance-carrying views over it.*

## The criticism of digital engineering is fair

Despite years of investment, many engineering organizations still struggle to articulate the return on digital engineering, and the skeptics have a point. In practice, DE is too often reduced to replacing Visio with more expensive diagramming software. Engineers spend months maintaining SysML models, then manually recreate the same information in PowerPoint, Word, Excel, and PDF because those are the artifacts the program actually reviews and delivers. When the model is just one more artifact that has to be synchronized with every other artifact, it is another document to maintain, at a higher license cost and with a smaller pool of people who can edit it.

I don't think the answer is to defend the tools. The answer is to notice that the industry picked the wrong unit of value. The opportunity was never to replace documents with models; it is to replace manually maintained engineering artifacts with generated views over a semantic engineering model. That distinction changes what engineers create, what organizations govern, and where engineering effort goes.

## The wrong mental model

Most organizations implicitly run this workflow: a requirements database feeds a SysML model, which feeds slide decks, which feed documents, matrices, and eventually a review package. The model sits in the middle of the chain as one deliverable among many.

[[FIGURE 1: The document-centric workflow. The model joins the artifact chain as one more deliverable, and every change propagates through manual re-synchronization.]]

Every hop in that chain is a manual copy, and every manual copy is an opportunity for drift. The architecture diagram, the traceability matrix, the interface document, the review slides, and the spreadsheet each hold their own version of the same facts, and consistency is maintained by attention rather than by construction. In defense programs the deliverable list itself (the CDRLs) reinforces the chain: the contract names documents, so the workflow produces documents, and the model becomes expensive documentation feeding a document factory.

## Treat the semantic model as the asset

Suppose instead that the semantic model, and nothing downstream of it, is the authoritative engineering asset. Every engineering fact exists exactly once: requirements, architecture, interfaces, behavior, verification, allocations, rationale, the relationships between design decisions and the simulations that support them. Everything else is a projection. Views, never copies.

[[FIGURE 2: The inverted pattern. Artifacts become regenerable views over the semantic model: queried on demand, validated on the way out, carrying provenance back to the baseline they rendered.]]

This is where SysML v2 earns its attention. Where earlier generations of MBSE tooling put the graphical notation first and the underlying data model a distant second, SysML v2 defines the semantic model as primary, with a textual notation and a standardized API in front of it. The model can be queried, transformed, validated, and integrated rather than only drawn. The diagram stops being the model; it becomes one projection of a database of engineering knowledge.

I'd push one step further than the SysML v2 ecosystem usually does. The projection machinery gets dramatically cheaper when the semantic substrate has global identity and a mature query and validation stack, which is exactly what the RDF technology family provides: URIs for identity, SPARQL for the query layer, SHACL for executable conformance checks, and PROV-O for recording what was generated from what. Whether the working store is a SysML v2 repository, a triplestore, or both bridged by the API matters less than the commitment that authority lives in the model and every rendering can be traced back to it.

## Documents become queries

Once engineering information exists semantically, many familiar artifacts stop being things anyone authors. Consider the requirements traceability matrix. Today it gets exported to Excel, where it begins drifting from reality the moment it lands. But an RTM has no independent content; it is a stored query. Against a reasonable vocabulary it is barely a screenful:

```sparql
PREFIX req: <https://example.org/engineering/>

SELECT ?requirement ?element ?method ?result WHERE {
  ?requirement a req:Requirement .
  OPTIONAL { ?requirement req:satisfiedBy ?element . }
  OPTIONAL {
    ?requirement req:verifiedBy ?activity .
    ?activity req:method ?method ;
              req:producedResult ?result .
  }
}
ORDER BY ?requirement
```

If those relationships exist in the model, the matrix should never be edited, only regenerated; and if they don't exist in the model, the matrix was fiction anyway. The same observation applies across the familiar deliverable set:

| Traditional artifact | Generated form |
|---|---|
| Requirements traceability matrix | A stored query over satisfaction and verification relationships |
| Interface control document | A rendered view of the interface subgraph |
| Architecture diagrams | Notation projections of structure |
| Verification matrix | An evidence traversal with results attached |
| Configuration lists | Composition views at a baseline |
| Allocation tables | Relationship queries |
| Review slide content | The current baseline, rendered to a template |
| Compliance reports | Conformance validation output |

The artifact ceases to be a source of truth. It becomes a rendering of the source of truth, stamped with when it was generated and, if the pipeline records provenance properly, exactly which model elements and which baseline it was generated from.

## Engineering effort moves onto the knowledge itself

This inversion changes where engineering hours go. Today an uncomfortable fraction of engineering effort is synchronization: updating diagrams, refreshing spreadsheets, rebuilding slides, checking that the Word document still agrees with the model, copying information between tools. Almost none of that advances the design.

In a semantic engineering environment that labor largely disappears, and the effort shifts to the knowledge: defining better relationships, capturing richer semantics, modeling assumptions explicitly, representing rationale, connecting simulation results to the decisions they support, strengthening verification evidence. The discipline starts to look like knowledge engineering, because that is what it is. From where I sit, that is a far better use of engineers than document production, and it is also a harder skill set than the industry currently hires for; I'll return to that below.

## The bigger prize is generated evidence

Documentation may turn out to be the lesser opportunity. Programs continuously ask questions like: which requirements remain unverified, which simulations support this design decision, what is affected by this requirement change, which interfaces moved since the previous baseline, which risks lack mitigation, what evidence supports compliance. Today these are answered by people assembling spreadsheets under deadline. Every one of them is a graph traversal. "Which requirements have no verification evidence" is a `FILTER NOT EXISTS` clause; "what changed since the last baseline" is a diff between two named graphs; "does this design conform to the interface standard" is a SHACL validation report rather than a checklist review.

A digital engineering environment built this way doesn't primarily generate documents. It generates evidence, on demand, from the current state of the model.

## Reviews without review books

Design reviews make the payoff concrete. Preparing for a PDR today can consume weeks of assembling the review package: slides updated, tables copied, figures recreated, matrices regenerated, interface lists refreshed. Review preparation becomes an exercise in document production, and the review examines the documents rather than the engineering.

If the baseline is semantic, a design review is a generated view of it: architecture projections, interface summaries, verification status, traceability, and most of the slide content produced from the model as it stands. Preparation time goes into improving the engineering baseline, because that is the only thing the package can render.

## Where AI actually fits

Large language models amplify this transition, and the direction of the amplification matters. An LLM bolted onto the document workflow becomes one more author of disconnected prose, generating polished artifacts that drift like all the others. Operating against the semantic model, it becomes the interface to the knowledge: "show every subsystem affected by this requirement," "which requirements have no verification evidence," "generate the ICD for this subsystem," "summarize architectural changes since the last baseline."

These are retrieval and reasoning tasks over a graph, with language generation only at the rendering step. That has a sobering corollary: the quality of the AI assistant is bounded by the quality of the engineering knowledge it operates over. A program with a thin, stale, or semantically sloppy model will get confident nonsense at machine speed. The model becomes the AI strategy.

## What has to be true before this works

I want to be direct about the friction, because the vision is easy to state and the path is not.

**The projection work moves; it does not disappear.** Someone must define and maintain the queries, view templates, and rendering pipelines that replace hand-authored documents. That is real engineering, and early on it can cost more than the documents did. The difference is that it amortizes: a view definition is written once and regenerated forever, while a document is re-edited forever.

**Generated artifacts still need configuration management.** A delivered ICD must be reproducible: which baseline, which query version, which template. Provenance recording is the mechanism that makes "regenerate it" an acceptable answer to an auditor, and it has to be designed in rather than bolted on.

**Contracts name documents.** CDRLs and DIDs specify deliverable documents, and a customer's acceptance process expects them. Until acquisition language accepts a rendered view of a governed model as satisfying a data item, programs will generate the document formats the contract names; the win in the near term is that generation replaces authorship, even while the deliverable list looks unchanged.

**Semantics are a skill, and vocabulary drifts.** Polished projections of a sloppy model are sloppy at higher production values. Someone has to govern identifiers, vocabularies, and modeling patterns across teams, and the people who can do that well are scarcer than diagram authors.

**The tooling is uneven.** SysML v2 API implementations are still maturing, and the rendering layer (model to document, model to deck, model to conformance report) is largely built per-program today. This will improve; it is not yet something a program adopts off the shelf.

## Organizational implications

None of this is only a tooling change. Engineers stop maintaining dozens of independent artifacts and start curating engineering knowledge. Configuration management shifts from document baselines toward semantic baselines. Quality assurance shifts from document review toward model validation. Review boards examine generated evidence rather than manually assembled books. Information architects and automation engineers become as consequential as diagram authors and document specialists, and the engineering organization gradually becomes a knowledge organization that happens to produce documents as a side effect.

## A more useful definition of digital engineering

Digital engineering is commonly described as "using models in engineering." That definition invites exactly the expensive-Visio outcome it should preclude. A more useful definition:

> Digital engineering is the practice of treating semantic engineering knowledge as the primary product, from which documentation, analysis, evidence, and decisions are generated.

Under that definition the value has nothing to do with drawing better diagrams. The value is in making engineering knowledge computable.

## Conclusion

For decades, documents have been treated as the product and models as supporting artifacts. The technology now exists to invert that relationship: the semantic model as the governed asset, and documents, matrices, review packages, and compliance evidence as generated, provenance-carrying views over it. The obstacles that remain are mostly organizational and contractual rather than technical, which historically means they are the slow ones. The programs worth watching are the ones whose count of manually maintained artifacts is going down.
