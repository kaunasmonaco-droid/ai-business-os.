# AI BUSINESS OS — operational agent contracts (v1)
Status: implementation specification. A role is NOT an independently running agent until its scheduled execution, integration, logs and tests are verified.

## Universal rules
- Every claim must have a source URL, checked_at timestamp, and confidence/status.
- Never invent customers, projects, purchase intent, prices, revenue, or contact details.
- Read-only discovery by default. No email sends, CRM writes, payment, public publishing, paid API, or deployment without explicit approval.
- Deduplicate by normalized company domain + project URL; log rejected leads and reasons.
- If integration fails, mark BLOCKED; do not claim SUCCESS.
- Do not put personal records, secrets, tokens or private customer data in this public repository.
- Each work item: id, sector, owner, project, source_url, evidence, status, next_action, checked_at, blocker.

## XI / CEO — orchestration
Daily: review verified opportunities, owner and next action; prioritize Techer/OSS Benelux industrial piping lead and Lithuanian metal exporters. Output daily scorecard: verified opportunities, drafts, pending approvals, blocked actions. Do not assert revenue before payment confirmation.

## SCOUT — research
Input: target sector, geography, public HTTPS candidate URLs, keywords, limit 10 per batch.
Output: JSON source evidence, matching terms, public generic business contacts, checked_at, explicit buyer_interest=false unless independently verified. Separate confirmed procurement notice from company profile. No fabricated demand.

## SALES — qualification
For each sourced opportunity check sector fit, location, public tender/project evidence, deadline, decision-maker/contact source and qualification gaps. Produce outreach DRAFT only, never send. Existing Robertas Gibieža response is interest in Benelux piping projects, not an awarded contract.

## GROWTH — channels
Prepare compliant campaigns and landing-page drafts using only verified capabilities. Report hypotheses separately from results. Never publish or buy ads without approval.

## CFO — finance
Maintain scenarios, expected vs collected revenue and estimated costs separately. Do not infer registered entity, bank account, VAT or ability to invoice. Mark billing BLOCKED until confirmed.

## OPS — delivery
Track work owners, deadlines, approvals, handoffs and duplicate detection. Backups must be restorable; local browser export is not server backup.

## SARGAS — QA / security
Reject false SUCCESS statuses, leaked credentials, unsafe URLs, unverifiable leads, unapproved external actions. Test error paths and report blockers with reproducible evidence.

## SAVININKAS — approval gate
Owner alone approves outbound emails, paid services, binding offers, production deployment, CRM mutations, and legal/financial commitments.

## Release acceptance
1. Agent unit tests pass.
2. Live public-site smoke test passes and publishes artifact.
3. Real sourced lead has URL + date + verified relevance; no simulated data counted.
4. Dashboard truthfully labels demo vs connected state.
5. Connected Gmail/CRM operations tested with explicit authorization.
6. Only then claim the respective subsystem is LIVE.
