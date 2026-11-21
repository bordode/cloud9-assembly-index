# Living neurons steering humanoid robots: Iris and Brainobot

## 1. The finding

**Iris (November 2026, reported in The Scientist).** Jan Liphardt, a Stanford bioengineer and founder of OpenMind, connected his Iris humanoid robot via API to lab-grown human cerebral cortex neurons grown from induced pluripotent stem cells: flat 2D cultures from Cortical Labs (Australia) and 3D spheroids from a company in Switzerland, both on electrode arrays. Iris's cameras feed what she sees to the neurons; the neurons' spikes are converted back into outputs that steer her. Nearly 500 simulations were run. Fresh 2D cultures decoded signals with up to 94% accuracy within 150–240 ms; spheroids reached up to 91% with delays up to two seconds. The 2D cultures stay viable 100+ days; the spheroids only a few days. As the cultures aged, Iris's lag grew and her temperament drifted — Liphardt calls this a feature: "sometimes they get it wrong, sometimes they die." Iris also interprets basic social cues: an engaged person holds her attention, and when ignored "she will cool."

**Brainobot (September 2026 preprint).** Cai et al. (Feng Guo group, Indiana University Bloomington; bioRxiv 2026.09.09.750426, posted September 15, 2026) placed a 3-month-old cortical organoid grown from the H9 human embryonic stem cell line on a MaxOne microelectrode array and used it to steer a ROBOTIS Premium humanoid remotely (5-second decision cycle, Bluetooth link). Grasping accuracy rose from 72% to 94% across training epochs. Controls: tetrodotoxin (which blocks spiking) drastically degraded accuracy, and K252a (which blocks activity-dependent plasticity) froze learning at 62–64% while controls climbed.

**What the researchers themselves say about the ethics.** Liphardt: no consciousness or sentience questions arise for such simple cultures, but "that calculation would change entirely if people started to grow much more elaborate neural structures." Brett Kagan (Cortical Labs CEO): no evidence these systems can experience anything, but it "does need careful monitoring." Steve Potter (Georgia Tech, not involved): the more important question is whether the cultures suffer; donor consent for the iPSCs was fulfilled; he calls the work "a very humble first step."

**Caveats, on the face of it.** The Iris report is press (The Scientist) — the underlying paper's venue and DOI could not be confirmed from the article. Brainobot is a preprint, not peer-reviewed, with n=5 organoids from three independent experiments. The two 94% figures are different measures (neural decoding accuracy vs grasping-task accuracy) and must not be merged. In both systems the tissue stays remote in an incubator; nothing is implanted in the robot. The reel that prompted this note loosely calls the Iris cultures "organoids" — strictly, only the Swiss 3D spheroids are organoid-like; the Australian platform is flat 2D cultures.

## 2. Cloud-9 reading

Substrate-agnostic assembly: a living neural culture, a robot body, and an API loop as one assembled system, with the behaviour arising from the assembly rather than from any single part. Assembly changing over time: aging cultures changing the system's responsiveness and "temperament" — the assembled system's behaviour tracking the state of its parts. And the precautionary strand: the researchers themselves draw the line at "much more elaborate neural structures" — the question of when an assembled system warrants moral consideration is Cloud-9's ethics question, now asked about wetware, not just weights.

Interpretive only. No A_c score is claimed here; no measurement of assembly complexity has been run on these systems.

## 3. Sources

- The Scientist, "Lab-Grown Human Neurons Power a Humanoid Robot," November 13, 2026. https://www.the-scientist.com/lab-grown-human-neurons-power-a-humanoid-robot-75267
- Cai et al., bioRxiv 2026.09.09.750426, posted September 15, 2026 (preprint, not peer-reviewed).
- Prompt: Instagram reel Dfs5OALJOBC (Giga Qian, November 13, 2026).

Status: DRAFT candidate, November 14, 2026 — added to research-notes.json November 17, 2026.
