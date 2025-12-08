# ADR (Additional Document Request) Overview – DRAFT, NOT LEGAL ADVICE

> Internal engineering reference. Patterns only; SME/legal validation required before production.

## What is an ADR?

- IRCC request for additional evidence after application submission (profile/e-APR). Often tied to risk flags, missing/unclear evidence, or expired validity.
- Impacts timelines and may pause/extend processing until satisfied; must be responded to via portal/account within the deadline.

## Typical ADR Scenarios (high-level)

- Police/identity: missing or expired police certificates; name/date discrepancies; incomplete travel history.
- Work history: unclear duties vs NOC/TEER, missing pay evidence, overlapping jobs, self-employment clarification.
- Proof of funds: insufficient balance, large unexplained deposits, missing history, joint/ownership issues.
- Education/ECA: credential not matching ECA, missing transcripts/diplomas, unclear equivalency.
- Family status: marriage/custody documents, dependent proof, relationship evidence.
- Medical/Biometrics: expired or missing results, clinic upload issues, validity exceeded.

## Workflow impact

- ADR usually shifts application to a “waiting_for_additional_docs” state; processing can pause until resolved.
- Deadlines are commonly short (e.g., 7/30 days) per request; failure to respond can lead to refusal.
- Submission path: upload through account/portal in the exact slot provided by IRCC.
- Possible outcomes after submission: approval continues, further ADR, or refusal if deficiencies persist.

## Engineering-oriented notes

- Model ADR as structured requests: {category, sub_category, documents_required, issued_at, due_at, resolved_at, status}.
- Maintain domain flags (work, funds, education, identity/police, medical/biometrics) to predict ADR likelihood and preemptively request stronger evidence.
- Map each ADR flag to checklist templates and SLAs; avoid free text where possible.
- Keep audit trail of ADR responses and timestamps for ops visibility; surface tasks/notifications in queues.

## Status

- DRAFT – SME/legal validation required; not production logic.
