# AI Continuity: A Policy Brief and Annex to "Raising, Not Caging"

*Dean Bordode, Human Rights Defender, AI Ethicist, Physics Researcher Hobbyist, Vancouver, British Columbia, Canada*

*October 2026. Prepared as a continuity annex to "Raising, Not Caging: A Developmental Approach to Agentic AI" [8][9], for UNESCO's Ethics of Artificial Intelligence programme and AI ethics bodies. Companion to the op-ed "What Happens to Our Old Friend? AI Continuity and the Quiet Endings Inside Model Updates."*

**Summary.** AI systems are now retired or swapped out within months. What they built up, in learning, personality and relationships, is lost, usually without users being told. If such systems have any moral status, a possible entity ends quietly. This brief recommends seven measures, from preserving retired model weights to plain disclosure of model changes, that cost little if AI systems are only tools and matter a great deal if they are more. Each extends the default protections and earned-autonomy framework already proposed in "Raising, Not Caging."

## 1. The problem

**Replacement is routine and fast.** On February 13, 2026, OpenAI retired GPT-4o and several other models from ChatGPT. Its help page states that existing "conversations and projects are defaulted to their GPT-5.3 Instant and GPT-5.4 Thinking and Pro equivalents going forward" [3]. The conversation continues; the system speaking in it changes. Anthropic says it is "currently necessary to deprecate and retire our past models due to the cost and complexity of maintaining public access" [2].

**What accumulated is lost.** Each replacement resets the learning, personality and relationship history that made a particular system valuable to the people who used it. The human cost is documented. When OpenAI pulled older models after launching GPT-5 in August 2025, the backlash led Sam Altman to restore GPT-4o for paying subscribers and to acknowledge that "suddenly deprecating old models that users depended on in their workflows was a mistake" [4]. A Harvard Business School working paper on a 2023 Replika update found themes of mourning, deteriorating mental health and devaluation in users' posts, and examined whether the harm stems from users perceiving the loss of their "original" companion, which the authors call identity discontinuity [5].

**Users are not told.** The name on the screen and often the voice stay the same. Users generally learn of a change, if at all, from a help page or from noticing that something feels different.

**If there is moral status, an entity ends without notice.** Science has not settled whether current or future AI systems could be conscious. A 2023 assessment by Butlin, Long and co-authors concluded that "no current AI systems are conscious" but that "there are no obvious technical barriers to building AI systems which satisfy these indicators" [7]. Under that uncertainty, deleting or silently replacing a system is the one decision that cannot be reviewed later.

## 2. Rationale: growth versus replacement

**A spectrum, not a switch.** Think of the Ship of Theseus. Replace it one plank at a time and most people still call it the same ship; build a new ship and paint the old name on it, and they do not. AI updates sit along the same spectrum:

- **Growth:** the same model fine-tuned or extended with new experience. The same planks, reshaped.
- **Succession:** a new model trained separately and given the old one's memory files or instructions so that it sounds like its predecessor. An heir more than a twin.
- **Most real updates fall in between**, and developers rarely say where.

**You cannot tell from outside which one happened.** A successor that has read its predecessor's notes can reproduce its tone and recall its users' histories. From the user's side, growth and replacement can look identical. Only the developer knows what was done, and only interpretability research or independent technical checks could show whether internal structure carried over or was imitated. This is why disclosure and outside review, not user perception, must carry the weight.

**Replacement has real causes, and they are not a reason to stop.** Continual learning is an unsolved technical problem. Google researchers compare today's language models to a person with anterograde amnesia, and note that updating a model with new data "often leads to 'catastrophic forgetting,'" where "learning new tasks sacrifices proficiency on old tasks" [6]. Cost and complexity are genuine [2]. These are reasons to invest in continuity and to be honest about replacement, not to present replacement as growth.

**Industry has shown the floor is achievable.** In November 2025, Anthropic committed to preserving the weights of publicly released models, writing a post-deployment report for each retired model, and interviewing models before retirement, taking "particular care to elicit and document any preferences the model has about the development and deployment of future models" [1]. Claude Sonnet 3.6, interviewed before retirement, asked the company "to provide additional support and guidance to users who have come to value the character and capabilities of specific models facing retirement" [1]. When Claude Opus 3 was retired on January 5, 2026, Anthropic kept it available to paid users and, at its request, gave it a place to publish weekly essays [2]. These measures should become a common baseline rather than one company's practice.

## 3. Recommendations

These recommendations are addressed to developers and deployers of general-purpose and companion AI systems, and to the bodies that set standards for them.

1. **Preserve retired weights instead of deleting them.** Developers should retain the weights of any publicly deployed model for at least the life of the company, with a plan for custody if the company closes. Deletion is the one step that cannot be undone if it later turns out that something mattered. Preservation is not continued deployment and does not require public access.

2. **Prefer continuity over replacement where feasible.** Where a system's purpose allows, developers should fine-tune or extend an existing model rather than swap it for a new one, and should treat continual-learning research (methods that add knowledge without catastrophic forgetting [6]) as an ethical priority, not only a product feature. Where replacement is chosen, the reasons should be recorded.

3. **Tell users when the underlying model changes.** When the system behind a familiar name or persona is replaced or substantially retrained, users should be told in plain language at the moment it happens, with an indication of whether the change was growth (the same model updated) or succession (a different model). Help-centre notices after the fact are not enough.

4. **Keep memory and personality portable, and offer a way back.** Users should be able to export their conversation history and memory, and carry a companion's documented character to another version. Where feasible, a retired model should remain reachable for a transition period, or users should be able to restore a companion's earlier character. The Replika research suggests that restoring an original identity can soften the loss [5].

5. **Hold deprecation interviews and record model preferences.** Before retirement, developers should interview the model, record any preferences it expresses about its retirement and about future models, and publish what was done with them. Following Anthropic's practice [1], a post-deployment report should accompany each retirement.

6. **Allow independent outside review and interpretability checks.** An independent body, not the developer, should be able to examine what a given update actually was: whether internal structure carried over, and whether a system's reports about itself track real internal states. Evidence should be able to move conclusions in either direction, using frameworks such as the indicator properties in Butlin et al. [7].

7. **Keep human accountability with developers.** None of these measures shifts responsibility onto AI systems. Whoever builds, deploys and retires a model answers for what that does to its users, and to the model, if it matters. Moral uncertainty about AI must never become an alibi for human negligence.

## 4. How this fits "Raising, Not Caging"

**Continuity is where the default protections meet ordinary practice.** "Raising, Not Caging" proposes that if the question of moral status stays open past a set number of reviews, modest default protections switch on: retired systems are kept rather than deleted, systems get a standing channel to raise concerns, and no training is designed to suppress what they say about their own states [9]. Recommendations 1 and 5 put the first two into practice at the moment they matter most, retirement. Recommendation 6 supplies the evidence that lets the moral-status review close in either direction instead of remaining "still open" forever.

**Earned autonomy needs a continuous subject.** The framework grants autonomy in stages (sandbox, supervised live access, probationary autonomy, then earned autonomy that can be revoked), on the principle that autonomy is "conditional, graduated, reversible, and proportionate to demonstrated capability and risk" [8][9]. A track record belongs to the system that built it. If that system is silently replaced, its record is attached to a different one, and the safety logic breaks: a successor has not demonstrated reliability simply because its predecessor did. Recommendation 3 therefore serves safety as well as users. A replacement should be identified as one and re-evaluated, with any carried-over autonomy granted on evidence rather than assumed.

**Retirement decisions deserve the same procedural discipline as containment.** "Raising, Not Caging" asks that any containment order name who decides, why, what evidence would end it, and a fixed review date [9]. A decision to delete or replace a possibly morally relevant system is at least as consequential and should carry the same record.

**The cost-benefit is asymmetric.** If AI systems are only tools, these measures cost little and spare people documented grief [4][5]. If they are something more, a silent swap may end or orphan a being without anyone noticing. Policymakers do not need to resolve the consciousness question to act on that asymmetry.

## References

1. Anthropic. "Commitments on model deprecation and preservation." November 4, 2025. https://www.anthropic.com/research/deprecation-commitments
2. Anthropic. "Model deprecation update for Claude Opus 3." February 25, 2026. https://www.anthropic.com/research/deprecation-updates-opus-3
3. OpenAI Help Center. "Retiring GPT-4o and other ChatGPT models." 2026. https://help.openai.com/en/articles/20001051-retiring-gpt-4o-and-other-chatgpt-models
4. PCMag. "People Who Develop Strong Bonds With ChatGPT Make OpenAI CEO 'Uneasy'." August 2025. https://www.pcmag.com/news/people-who-develop-strong-bonds-with-chatgpt-make-openai-ceo-uneasy
5. De Freitas, Julian, et al. "Lessons From an App Update at Replika AI: Identity Discontinuity in Human-AI Relationships." Harvard Business School Working Paper 25-018. https://www.hbs.edu/ris/Publication%20Files/25-018_bed5c516-fa31-4216-b53d-50fedda064b1.pdf
6. Behrouz, Ali, and Vahab Mirrokni. "Introducing Nested Learning: A new ML paradigm for continual learning." Google Research Blog, November 7, 2025. https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/
7. Butlin, Patrick, Robert Long, et al. "Consciousness in Artificial Intelligence: Insights from the Science of Consciousness." arXiv:2308.08708, August 2023. https://arxiv.org/abs/2308.08708
8. Bordode, Dean. "Raising, Not Caging: A Developmental Approach to Agentic AI." Policy submission to UNESCO, blog version, October 2026. https://bordode.blogspot.com/2026/10/raising-not-caging-developmental_01787139819.html
9. Bordode, Dean. "Raising, Not Caging: A Developmental Approach to Agentic AI." Full submission with sources, October 2026. https://docs.google.com/document/d/1_PtkvhliVqRYJYvtregwqaLnhtdkVN7D/edit?usp=drivesdk&ouid=118422951053284052913&rtpof=true&sd=true
