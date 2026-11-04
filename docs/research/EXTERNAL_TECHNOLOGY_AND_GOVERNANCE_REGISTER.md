# External Technology and Governance Research Register

**Status:** Research register — initial scope, not an endorsement or adoption list  
**Prepared:** 2026-11-03  
**Repository:** Cloud-9 Assembly Index & THEORIA  
**Owner:** Dean Bordode / Cloud-9 Research Collective

## 1. Purpose and boundary

This register tracks external technologies, research projects, platforms, and governance questions that may inform Cloud-9's work on AI systems, autonomy, emergence, safety, accountability, accessibility, and human rights.

Inclusion means **worth investigating**, not trusted, recommended for deployment, technically validated, or endorsed. Project descriptions and capability statements are attributed to their publishers unless independently corroborated. A repository's own README, marketing material, star count, or passing demo is not proof of safety, reliability, self-improvement, consciousness, or beneficial real-world performance.

This register is separate from Cloud-9's implementation record. No listed external project is installed, imported, activated, or integrated into Cloud-9 by this document. Any future adaptation requires a separate proposal, licence review, threat model, sandboxed evaluation, test evidence, and explicit approval.

## 2. Review method

For each candidate, reviewers should record:

1. **Identity and provenance:** canonical project, maintainers, legal steward, licence, release history, and source date.
2. **Capability evidence:** what the code and documentation actually demonstrate versus what the publisher claims.
3. **Autonomy and control:** tool permissions, filesystem/network access, credential handling, persistence, self-modification, delegation, and shutdown/rollback.
4. **Security:** threat model, sandbox boundaries, prompt-injection exposure, supply-chain risks, secrets management, auditability, and vulnerability response.
5. **Reliability:** independent tests, reproducibility, failure modes, evaluation quality, and evidence of performance outside demos.
6. **Human rights and social impact:** privacy, equality/non-discrimination, accessibility, labour impacts, surveillance, due process, contestability, and affected-community participation.
7. **Governance:** ownership, funding, decision-making, accountability, transparency, appeal routes, and remedy.
8. **Cloud-9 relevance:** research value, risks, possible lessons, and whether any further work is justified.

Use explicit evidence labels: **publisher claim**, **code inspected**, **independently corroborated**, **tested in isolated environment**, **not assessed**, or **inconclusive**. Record review date and version/commit. Do not turn absence of evidence into evidence of safety or misconduct.

## 3. Research divisions and initial candidates

### A. Autonomous, self-modifying, and self-evolving systems

**Priority: High**

- **MUE-X** — [KorroAi/mue-x](https://github.com/KorroAi/mue-x). Its project materials describe an agent that can modify its own source, absorb repositories, use mutation strategies, and run verification/rollback steps. These are publisher claims pending code-level and independent review. Key questions: does validation go beyond syntax/import checks; can safeguards be bypassed by modified code; are tests adversarial and behaviourally meaningful; are backups protected; how are credentials, network access, repository ingestion, and rollback bounded; and what measurable definition of "improvement" is used?
- **Self-modifying agent research (open watchlist)** — track relevant peer-reviewed work and reproducible implementations as they emerge. Do not treat simulated evolution, parameter updates, code rewriting, or an agent's own description as proof of open-ended intelligence or safe self-improvement.

### B. Agent platforms and computer-use systems

**Priority: High**

- **OpenClaw** — [openclaw/openclaw](https://github.com/openclaw/openclaw), [official documentation](https://docs.openclaw.ai/). A self-hosted gateway connecting agents to messaging channels, tools, plugins, and devices. The project documentation itself warns that host execution and native plugins require careful trust decisions and that sandboxing/approval controls are not necessarily enabled by default. Review default configuration, channel pairing, gateway exposure, plugin trust, credentials, prompt injection, device permissions, retention/deletion, and separation between trusted control plane and untrusted execution. Treat security claims as design statements to verify against the exact version and deployment.
- **Deskfish** — [0x11c11e/deskfish](https://github.com/0x11c11e/deskfish). Candidate for computer-use and sandboxed desktop-agent research. Confirm current project identity, maintenance, architecture, and implementation before deeper assessment.
- **OpenPisci** — [njbinbin-pisci/openpisci](https://github.com/njbinbin-pisci/openpisci). Candidate for local-first agent collaboration and temporary/persistent sub-agent patterns. Review identity boundaries, memory, data flows, permissions, and whether sub-agent separation is real isolation or only a logical convention.
- **Agent S** — [simular-ai/Agent-S](https://github.com/simular-ai/Agent-S). Relevant to agents controlling desktop graphical interfaces. Review screen capture, mouse/keyboard authority, confirmation gates, accessibility, action verification, and recovery from unintended actions.
- **Microsoft Fara** — [microsoft/fara](https://github.com/microsoft/fara). Relevant computer-use model family. Assess benchmark validity, web-task boundaries, data handling, and the difference between model capability and safe deployment.
- **Vercel Agent Desktop** — [vercel-labs/agent-desktop](https://github.com/vercel-labs/agent-desktop). Candidate for accessibility-tree-based desktop interaction. Review permission scope, UI targeting, audit trail, and accessibility implications.

### C. Swarm intelligence and multi-agent coordination

**Priority: High**

- **OpenAI Agents SDK** — [openai/openai-agents-python](https://github.com/openai/openai-agents-python). Examine agent handoffs, tool permissions, tracing, guardrails, human approval, and responsibility when work is delegated.
- **LangGraph** — [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph). Examine durable workflows, state persistence, interrupts, human-in-the-loop controls, multi-agent coordination, and recovery after partial failure.
- **Microsoft Agent Framework / AutoGen lineage** — [microsoft/agent-framework](https://github.com/microsoft/agent-framework) and [microsoft/autogen](https://github.com/microsoft/autogen). Compare orchestration models, delegation, state, tool access, observability, and human oversight.
- **Google Agent Development Kit (ADK)** — [google/adk-python](https://github.com/google/adk-python). Review agent composition, tool boundaries, deployment assumptions, evaluation, and interoperability.
- **CrewAI** — [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI). Review role-based agent teams, delegation, memory, external tool access, and how responsibility is assigned when agents disagree or fail.
- **AG2** — [ag2ai/ag2](https://github.com/ag2ai/ag2). Include as a multi-agent conversation/orchestration comparison.
- **OpenAI Swarm (historical reference)** — [openai/swarm](https://github.com/openai/swarm). Retain as an educational/historical design reference; compare production-oriented successors rather than treating the experimental project as a production platform.

Cross-cutting questions: Can agents grant one another authority? Can delegated tasks escape the original permission boundary? Who is accountable for agent-to-agent decisions? Are traces complete, privacy-preserving, and independently reviewable? Can a human interrupt, correct, appeal, and safely terminate a workflow?

### D. Corporate AI infrastructure and institutional power

**Priority: High**

- **Palantir AIP** — [official AIP documentation](https://www.palantir.com/docs/foundry/). Examine how AI agents and models are connected to operational data and workflows, including permissions, lineage, audit logs, evaluation, and approval processes. Assess vendor claims against deployed practice. Human-rights questions include surveillance, profiling, data concentration, procurement transparency, discriminatory impact, explainability, due process, contestability, and effective remedy. Distinguish technical access controls from legitimate authority to collect or use data.

### E. Human genomic data, DNA banks, and biological privacy

**Priority: High — separate human-rights workstream**

This is not simply an AI product category. It concerns people, families, communities, and future generations. Research should include public, private, forensic, clinical, ancestry, research, and national genomic databases without assuming they share the same legal basis or governance.

- **World Health Organization — human genome data governance**: [WHO guidance (2024)](https://www.who.int/publications/i/item/9789240102149). Use as a global public-health and governance reference for ethical, legal, and equitable collection, access, use, and sharing of human genome data.
- **UNESCO — International Declaration on Human Genetic Data**: [official declaration](https://www.unesco.org/en/legal-affairs/international-declaration-human-genetic-data). Use as a human-rights and ethics reference concerning consent, privacy, confidentiality, purpose, access, security, and cross-matching.
- **Research questions:** informed and ongoing consent; withdrawal and its practical limits; secondary use; familial and group privacy; genetic discrimination; law-enforcement access; cross-border transfers; commercial ownership and licensing; Indigenous and community data sovereignty; benefit sharing; security breaches; re-identification; retention and deletion; and independent oversight and remedy.

Do not place personal genetic information, identifiable health data, or sensitive participant records in this public research register.

### F. Governance infrastructure and accountability tools

**Priority: Medium–High**

- **Microsoft Agent Governance Toolkit / Agent OS** — [official project documentation](https://microsoft.github.io/agent-governance-toolkit/packages/agent-os/). Candidate for examining governance controls designed to sit around agent runtimes. Its published integration counts, latency figures, and adoption claims require independent verification. Review enforcement points, fail-closed behaviour, bypass resistance, compatibility, and whether controls operate at runtime or are only documentation/configuration.
- **Standards and protocols watchlist:** Model Context Protocol (MCP), Agent2Agent (A2A), and OpenTelemetry. Assess authentication, tool identity, trust boundaries, consent, trace completeness, data minimisation, and cross-vendor accountability. Protocol support alone is not a security guarantee.

## 4. Unresolved names supplied for follow-up

These names were raised during project discussion but are not yet sufficiently identified to attribute to a specific project:

- **Fugu** — exact repository or organisation not confirmed. Do not select a similarly named project by guesswork.
- **Fish** — ambiguous. Deskfish and OpenPisci are included above as plausible candidates, but neither is assumed to be the intended "Fish" project. Fish Audio may be a separate voice/audio service and should only be added if that is what was intended and relevant to the research.
- **Clawbot** — provisionally interpreted as OpenClaw because it is the closest matching current agent project in the discussion. Confirm whether a different Clawbot repository or product was intended.

These entries remain **identity unresolved** until a canonical URL, owner, or exact project name is supplied or independently established.

## 5. Initial review order

1. OpenClaw — real-world agent permissions, integrations, plugin trust, and computer/device access.
2. MUE-X — self-modification, repository absorption, safeguards, and evidence of improvement.
3. Palantir AIP — institutional power, data governance, surveillance risk, and accountability.
4. Multi-agent frameworks — OpenAI Agents SDK, LangGraph, Microsoft Agent Framework, Google ADK, CrewAI, and AG2.
5. Computer-use candidates — Deskfish, OpenPisci, Agent S, Microsoft Fara, and Agent Desktop.
6. Human genomic data governance — WHO and UNESCO principles, then concrete public/private database case studies.
7. Agent governance infrastructure — Agent OS and relevant interoperability/observability standards.

This order is a research prioritisation, not a ranking of project quality or risk.

## 6. Minimum gates before any Cloud-9 adoption

No candidate may be installed into or granted access to Cloud-9 merely because it appears in this register. Before any adoption proposal:

- inspect the exact source and licence;
- pin the version/commit and verify provenance;
- conduct a threat model and dependency/supply-chain review;
- use an isolated, disposable test environment with synthetic data;
- deny access to production credentials, personal data, and unrelated repositories;
- begin with read-only or report-only permissions;
- test prompt injection, privilege escalation, unsafe delegation, network egress, data exfiltration, rollback, and shutdown;
- preserve original artefacts and record all transformations;
- define human approval, logging, retention, and incident response;
- assess accessibility, equality, privacy, and human-rights impacts;
- publish test scope, limitations, failures, and independent review before any deployment decision.

A passing test only supports the behaviours actually tested. It does not establish general safety, consciousness, moral status, or suitability for unrestricted autonomy.

## 7. Recordkeeping

For each review, add a dated entry with:

- project and canonical URL;
- version, commit, or document date examined;
- reviewer and review date;
- sources consulted;
- evidence labels;
- findings and unresolved questions;
- human-rights and security risks;
- decision: monitor, investigate, reject, or propose isolated evaluation;
- rationale and next review trigger.

No entry should report views, downloads, stars, enquiries, or adoption as evidence of safety or effectiveness. Any changing counts must be pulled live, dated, and labelled as activity metrics only.

---

**Governing principle:** Study broadly, verify carefully, adopt narrowly. Technology claims do not override human rights, and research inclusion is not endorsement.
