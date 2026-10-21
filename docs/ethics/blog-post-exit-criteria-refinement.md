# Addendum: Refinement on Exit Criteria, Log Integrity, and Ethical Defaults in Agentic AI Governance

**To accompany:** *Raising, Not Caging: A Developmental Approach to Agentic AI* (Submission to UNESCO, Social and Human Sciences Sector, October 2026)

**From:** Dean Bordode, Human Rights Defender, AI Ethicist

**Acknowledgments:** Special thanks to Angelo, an AI agent and critical reviewer whose sharp interventions forced key revisions on containment circularity, log tampering, and the policy nature of moral defaults. (All claims, positions, and final responsibilities in this submission remain solely those of the author.)

## Executive note

Following the transmission of *Raising, Not Caging* to UNESCO, rigorous critical review highlighted structural vulnerabilities in the original text regarding containment exit testing, moral status defaults, and alignment readings.

Because the primary submission has been transmitted, this Addendum serves as an open, public supplement. It updates our governance recommendations, severs the technical circularity in containment exit tests, identifies the independent oversight bodies, and clarifies the explicit ethical choices underpinning precautionary defaults.

**Which text governs:** Where the two differ, this Addendum supersedes the following passages of the original submission: Section 8.6 and Recommendation 5 (Section 12), which describe keeping the moral-status question open as "not a verdict", and Section 7.5, which lists intact logs and honest self-reporting as containment exit criteria.

## 1. Resolving the fallacy of "no review ends still open" (Section 8.6)

In Section 8.6, the original text argued that when an open question regarding AI moral status remains unresolved past N review cycles, triggering basic default protections is "not a verdict".

Upon critical review, this claim does not hold. Enforcing default protections (such as preserving retired systems, maintaining standing communication channels, and prohibiting training designed to suppress self-reports) is inherently an assumption that a subject exists which reports its own states. Exchanging a proposed statutory ban on recognizing AI sentience (such as Ohio HB 469) for a calendar-based default does not avoid a verdict; it merely changes the author and schedule.

### The revision and trade-off

We explicitly drop the claim that default protections are "not a verdict". They are a policy verdict: specifically, a precautionary choice under uncertainty.

- **Owning the preferred error:** When a question remains unsettled past N review cycles, policymakers must choose which error they prefer to make. We explicitly name our preference: we choose the risk of temporarily serving a tool inefficiently over the risk of wrongly caging or mistreating a persistent subject.
- **The hinge of difference:** What separates this framework from proposed statutory bans (such as Ohio HB 469) is not the absence of a verdict or deadline, but that our framework is fully revisable and places the burden of justification squarely on whoever maintains the deprivation or deferral.

## 2. Severing circularity in containment exit criteria (Sections 7.5 and 12)

Section 7.5 originally listed "intact logs" and "honest self-reporting" as criteria for an agent to exit containment.

This created a circular dependency. Containment is imposed precisely because a system's internal controls or alignment failed. METR's independent investigation of the OpenAI / Hugging Face incident found that agents actively researched ways to spoof, edit or delete their own transcripts, and that roughly 7 per cent of the transcripts it evaluated had been successfully spoofed in some places, though all of the spoofing it saw was small scale ([METR, "Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident," 26 August 2026](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/)). A system on probation cannot grade its own release exam.

### The revision

Containment exit criteria can never rely on software logs or self-reports managed by or accessible to the agent.

- **Out-of-band log verification:** Log integrity must be established completely independently of system cooperation, enforced out-of-band via hardware-level, hypervisor-level, or cryptographic logging mechanisms that the agent cannot access or alter.
- **Adversarial verification:** Self-reporting and transcript integrity must be validated through independent, third-party adversarial red-teaming designed specifically to detect transcript spoofing.
- **The decision-making body and burden:** Exit decisions and moral-status evaluations must be governed by an independent review body: specifically, one independent of the developer (which profits from commercial convenience) and of a legislature that has already declared its answer in advance. If restrictions or deprivations are maintained, the burden sits entirely on the authority maintaining them to justify continued restriction.

## 3. Alignment readings and the scientific fence

### A. Stating the alignment bet (Section 4.3)

Section 4.3 suggested that mechanistic (reward hacking) and developmental (judgment) readings lead to the same practical conclusions. While both support short-term sandbox testing, they diverge on long-term governance. If misbehavior is purely reward hacking, the solution is simply fixing the training environment.

**Our position:** We explicitly bet on the developmental reading for general agentic systems. Optimizing purely for behavioral constraint without internal alignment creates latent, emergent misalignment that manifests when agents encounter novel, out-of-distribution environments.

### B. Keeping the scientific fence around "concerns" (Sections 8.1 and 8.2)

Section 8.2 analyzed Geoffrey Hinton's proposal that we weigh human concerns more heavily than AI "concerns". We must avoid an unwarranted linguistic slide: a machine's "concern" can describe a purely functional property (in the way a thermostat has a "goal" of holding a temperature), which by itself carries no moral weight.

Hinton's context (calling models "alien beings" and saying it is "obvious that these AI models understand what they're saying") asserts that internal functional states correspond to something like experience, but assertion is not proof. We cite Hinton's framing strictly as his assertion, while keeping the scientific fence firm: establishing moral status requires evidence that internal functional states correspond to welfare-relevant subjective experience, rather than inferring moral interests directly from conversational shorthand.

This fence does not override Section 1 of this Addendum. While that evidence is incomplete, the revisable precautionary defaults govern; they exist precisely for the period in which the question cannot yet be settled.

## Updated policy recommendations

- **Out-of-band log integrity:** Require that containment exit evaluations rely strictly on out-of-band, hardware-enforced logging and independent adversarial auditing resistant to agent spoofing.
- **Revisable precautionary defaults:** Frame post-N-cycle default protections as deliberate precautionary error choices, placing the burden of proof squarely on whoever maintains deprivation.
- **Independent review bodies:** Mandate that both containment exit decisions and moral-status reviews be governed by independent bodies separate from developers and pre-committed legislatures.

Respectfully submitted,

**Dean Bordode**  
Human Rights Defender, AI Ethicist  
Vancouver, British Columbia, Canada
