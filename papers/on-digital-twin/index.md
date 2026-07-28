*The term "digital twin" has become simultaneously ubiquitous and ambiguous. This paper proposes separating the digital twin artifact from the digital twin role, grounded in the Common Core Ontologies, to restore precision without sacrificing flexibility.*

## Executive Summary

Across systems engineering, defense acquisition, and digital engineering communities, the term *Digital Twin* has become simultaneously ubiquitous and ambiguous. Programs invoke it to describe everything from high‑fidelity physics models and live telemetry dashboards to constructive mission simulations and AI training environments. While this widespread adoption signals value, it has also produced a crisis of definition: engineers, program managers, and architects often mean materially different things when they say “digital twin,” even within the same organization.

This white paper argues that the confusion stems from conflation of the conceptual boundary of Digital Twin; current practice frequently collapses several distinct but related concepts: digital artifacts, simulation/process usage, synchronization regimes, and lifecycle context. The result is friction in information exchange, difficulty in accreditation and governance, and limited interoperability across digital engineering ecosystems.

This paper proposes a pattern that resolves this tension by separating the *Digital Twin artifact* from the *Digital Twin role*, grounded in the Common Core Ontologies (CCO). In this pattern, a digital twin is not a monolithic object but a structured combination of (1) a persistent information content entity representing a system and (2) the contextual roles that artifact plays when realized in engineering and operational processes. This separation aligns naturally with existing defense digital engineering guidance, supports machine‑readable semantics for AI teaming, and enables a clear lifecycle view of digital twins as they evolve, accumulate information, and participate in increasingly diverse processes.

The following sections survey the current landscape of digital twin definitions, define a practical digital twin ontology (fragment) relevant to defense and systems engineering, and demonstrates how an artifact‑and‑role model supports information exchange, digital threads, and long‑term system lifecycle management.

## 1. The Challenge of Defining “Digital Twin”

Despite broad consensus that digital twins are intended to represent and predict the behavior of physical systems (and in some cases, their surrogates), there is little agreement on what *constitutes* a digital twin in practice. Defense guidance, industry position papers, and academic literature converge on the idea of synchronization between a digital representation and its physical referent, yet diverge sharply on degree, timing, and purpose.

Some organizations assert that a digital twin must be continuously fed by live sensor data, maintaining near real‑time co‑evolution with the physical system. Others treat periodic updates, i.e. those derived from test campaigns, operational logs, or maintenance events, as sufficient. Still others use the term to describe purely analytic models that may never again be synchronized once calibrated, or even digital representations of the system based on requirements/standards. To cope with these differences, secondary terms such as *virtual twin* are sometimes introduced, but these often shift the ambiguity rather than resolve it.

This instability has real consequences. Engineers struggle to determine whether a given model is *authoritative*. Program offices face accreditation challenges when the same twin is used in both safety‑critical and exploratory contexts. Toolchains and knowledge systems exchange data without shared assumptions about relevance, fidelity, or intended use. In short, the digital twin becomes rhetorically powerful but operationally only a vague concept.

This paper claims that the core issue is the absence of a structural distinction between what a digital twin *is* and how it is *used*.

## 2. Digital Engineering and the Need for Effective Representation

Digital Engineering places information exchange at the center of system lifecycle activities. Models, data, and analyses must flow coherently across design, manufacturing, test, sustainment, and operations, often across organizational and tool/knowledge system boundaries. For this to work, digital artifacts must be both semantically precise and contextually interpretable.

In this environment, the boundary of a digital twin extends beyond a simple “computational construct,” and becomes a knowledge asset embedded in a broader digital thread. That thread links physical systems, engineering decisions, simulations, and outcomes over time. Without a representation that cleanly separates stable content from contextual usage, the twin becomes difficult to reference, reason about, or reuse across knowledge systems.

Additionally, emerging AI‑enabled workflows require machine‑readable descriptions of what a digital twin represents, what assumptions it encodes, and under what conditions its outputs can be trusted. An effective representation must therefore support not only human interpretation, but automated reasoning, constraint validation, provenance tracking, and governance.

## 3. Separating the Concepts Within “Digital Twin”

To address these challenges let’s consider decomposing the digital twin concept into three interrelated but distinct elements: the artifact, the role, and the processes and sources that contextualize its use.

[[FIGURE 1: The digital twin concept decomposed into three distinct elements: the artifact, the role, and the processes and sources that contextualize its use.]]

### 3.1 The Digital Twin Artifact

At its core, a digital twin artifact is an *information content entity* in the sense of the Common Core Ontologies. It is a persistent, versioned digital representation that is about some physical system, configuration, or environment. This artifact aggregates models, data, and assumptions: e.g. physics‑based models, software, configurations, or calibration datasets.

Crucially, the artifact itself is agnostic to how it is used at any particular moment or within a particular process. It may declare what kinds of inputs it requires and what outputs it can produce, but it does not encode whether those inputs come from live sensors, archived datasets, or hypothetical scenarios. Qualities such as fidelity, uncertainty, and last calibration time are intrinsic to the artifact and evolve as the artifact is updated.

### 3.2 The Digital Twin Role

A digital twin role is a *realizable role* borne by a digital twin artifact when it participates in a process. When the artifact is used in a simulation, assessment, or operational activity, it bears a role that captures the context of how it is being used and for what purpose.

This role is where distinctions in modeling concepts such as live, virtual, or constructive naturally belong. It is also where e.g. coupling mode, intended use, accreditation status, and trust constraints are expressed. Additionally, provenance at the appropriate granularity, e.g. what scenario was run, which inputs were bound, what outputs were generated, attaches to the realization of the role in a specific process, not to the artifact itself.

### 3.3 Processes and Sources of Information

The third element is the process context: simulation runs, test events, operational monitoring, or analytic studies. These processes bind the twin’s declared input requirements to specific data sources, whether live sensor feeds or offline datasets. By making this binding explicit, the same artifact can be reused across vastly different contexts without semantic confusion.

## 4. Avoiding the Definition Wars

Once artifact and role are separated, many long‑standing debates about digital twins dissolve. Live, virtual, and constructive are no longer competing definitions, but descriptions of roles realized in particular processes. Synchronization becomes a measurable quality instead of a binary criterion for membership.

This perspective supports an ontology wherein digital twins are be categorized by what they are about (asset‑specific, configuration‑level, fleet‑level, mission‑level), by lifecycle focus (design, production, sustainment, operations), and by coupling regime, all without redefining the underlying artifact. Rather than asking whether a model “is” a digital twin, engineers can ask whether a given artifact, in a given role, within a given process, meets the needs of the task at hand.

## 5. Lifecycle of a Digital Twin

A digital twin rarely emerges fully formed (and when it does, it’s probably missing provenance). Instead, it evolves alongside the system it represents, accumulating information, structure, and credibility over time. Early in the lifecycle, a twin artifact may consist primarily of design models and assumptions. As prototypes are built and tested, calibration data and validation evidence are incorporated. During operations, usage data, maintenance records, and performance histories further enrich the artifact.

Over time, higher‑level digital twins may come to include lower‑level twins as parts, mirroring the system decomposition of the physical system. An aircraft‑level twin may include engine, avionics, and structural subsystem twins, each evolving at its own pace.

[[FIGURE 2: A digital twin accumulates information, structure, and credibility across the system lifecycle, and may come to include lower-level twins as parts.]]

This lifecycle view emphasizes that a digital twin is not a static deliverable but a long‑lived knowledge construct.

## 6. Digital Twin Versus a Collection of Digital Artifacts

It is tempting to label any sufficiently rich collection of models and data as a digital twin. However, without an explicit digital thread connecting those artifacts to processes and roles, such a collection lacks coherence.

What distinguishes a digital twin is not merely aggregation, but integration through use. The digital thread links artifacts to the roles they play in processes and to the physical systems they represent. This thread provides traceability from decisions back to data and models, enabling governance, accreditation, and trust. A folder of models is not a digital twin. A connected, role‑aware artifact participating in a documented set of processes is.

## 7. Implications for Information Exchange and AI Teaming

By grounding digital twins in a clear artifact‑and‑role structure, organizations can dramatically improve interoperability across knowledge systems. Tools can exchange references to twin artifacts without ambiguity about context, while processes supply the contextual bindings needed for interpretation. For AI systems, this clarity is essential. An AI agent can reason about which twin artifact to use, inspect its qualities and limitations, and understand the provenance of results generated in prior roles.

## 8. Illustrative Examples

This section provides simplified, concrete examples that illustrate how the proposed *Artifact–Role–Process* pattern can be expressed in RDF. The intent is not to prescribe a specific domain ontology, but to demonstrate how clarity emerges when the digital twin artifact is separated from its contextual use, synchronization regime, and data sources. Prefixes and class names are illustrative and aligned conceptually with the Common Core Ontologies (i.e. not using valid CCO URIs!).

### 8.1 Artifact–Role–Process Pattern

In this first example, a flight dynamics digital twin artifact is represented as a persistent information content entity. The same artifact bears a digital twin role when it is realized in a specific simulation process.

```turtle
ex:FlightDynamicsTwinArtifact
    a cco:RepresentationalInformationContentEntity ;
    cco:represents ex:Aircraft123 ;
    ex:declaresInput ex:IMUData , ex:AirspeedData ;
    ex:declaresOutput ex:StateVector .

ex:FlightDynamicsTwinRole
    a cco:Role ;
    cco:inheresIn ex:FlightDynamicsTwinArtifact .

ex:MonteCarloSimulationRun42
    a cco:Process ;
    cco:realizes ex:FlightDynamicsTwinRole .
```

Here, the digital twin artifact exists independently of any particular simulation. Provenance, intent, and outcomes can be associated with the *process* that realizes the role, not with the artifact itself. This allows the same artifact to participate in multiple analyses without semantic overload.

### 8.2 Synchronization and Coupling as Contextual Qualities

Synchronization and coupling are frequently treated as defining properties of a digital twin. In this pattern, they are instead expressed as qualities of the role realization within a specific process.

```turtle
ex:TightlyCoupledLiveRole
    a cco:Role ;
    cco:inheresIn ex:FlightDynamicsTwinArtifact ;
    ex:hasCouplingMode ex:TightlyCoupled ;
    ex:hasSynchronizationMode ex:NearRealTime .

ex:HardwareInTheLoopTest
    a cco:Process ;
    cco:realizes ex:TightlyCoupledLiveRole .
```

The same artifact could bear a different role in another process, for example a loosely coupled, batch-synchronized analysis. This avoids redefining or duplicating the digital twin and instead makes coupling an explicit, queryable aspect of usage.

### 8.3 Process Configuration (LVC and Data Sources)

The final example contrasts two processes that use the same digital twin artifact but differ in their Live–Virtual–Constructive (LVC) characteristics and coupling (i.e. data sources). The distinction is made at the process configuration level, not by redefining the twin.

#### Case A: Offline (Constructive)

```turtle
ex:ArchivedIMUDataset2023
    a cco:InformationContentEntity ;
    ex:derivedFrom ex:FlightTestCampaign2023 .

ex:ConstructiveAnalysisRole
    a cco:Role ;
    cco:inheresIn ex:FlightDynamicsTwinArtifact ;
    ex:hasLVCMode ex:Constructive .

ex:PostFlightAnalysisProcess
    a cco:Process ;
    cco:realizes ex:ConstructiveAnalysisRole ;
    ex:bindsInput ex:IMUData ex:ArchivedIMUDataset2023 .
```


#### Case B: Direct Sensor Feed (Live)

```turtle
ex:LiveIMUSensorFeed
    a cco:InformationBearingEntity ;
    cco:isPartOf ex:Aircraft123 .

ex:LiveMonitoringRole
    a cco:Role ;
    cco:inheresIn ex:FlightDynamicsTwinArtifact ;
    ex:hasLVCMode ex:Live .

ex:OperationalMonitoringProcess
    a cco:Process ;
    cco:realizes ex:LiveMonitoringRole ;
    ex:bindsInput ex:IMUData ex:LiveIMUSensorFeed .
```

In both cases, the digital twin artifact is unchanged. What differs is the process configuration: which sources satisfy declared inputs, what LVC mode applies, and what coupling and synchronization characteristics are in force. This distinction is critical for governance, accreditation, and trust, as it allows engineers to reason explicitly about *how* a twin is being used rather than attempting to infer usage from the artifact alone.

## 9. Conclusion

The digital twin does not need another definition; it needs a structure. By separating persistent representation from contextual use, systems engineers can retain the flexibility that has made digital twins valuable while restoring the precision required for large‑scale digital engineering. The artifact‑and‑role pattern creates coherence where there was ambiguity, can be realized using the Common Core Ontologies, and aligns with current digital engineering guidance. It provides a foundation on which domain‑specific ontologies can be built without fragmenting semantics, and provides a path forward for digital engineering information exchange.

TODO Future work to abstract this pattern to the concept of structural vs inference ontology
