---
name: report-writing
description: Bug bounty report writing for H1/Bugcrowd/Intigriti/Immunefi — report templates, human tone guidelines, impact-first writing, CVSS 3.1 scoring, title formula, impact statement formula, severity decision guide, downgrade counters, pre-submit checklist. Use after validating a finding and before submitting. Never use "could potentially" — prove it or don't report.
---

# REPORT WRITING

Impact-first. Human tone. No theoretical language. Triagers are people.

---

## PRE-REPORT PROGRAM ANALYSIS (do this BEFORE writing any report)

Before drafting a single sentence, read the full program brief and extract:

```
1. SUBMISSION RULES
   - Required email domain (e.g., @bugcrowdninja.com)
   - Attachment policy (screenshots OK? videos? binaries?)
   - AI-generated report policy (concise? ban?)
   - Scanner output policy (most programs reject raw scanner output)
   - One vulnerability per report rule

2. FOCUS AREAS
   - What the program explicitly prioritizes (e.g., "cross-client data access")
   - What they pay most for (read reward tiers per target)

3. OUT-OF-SCOPE ITEMS
   - Specific VRT exclusions (e.g., "Application-Level DoS = Out-of-Scope")
   - Domain/hosting exclusions (e.g., "fly.io issues → report to fly.io")
   - Behavioral exclusions (e.g., "do not report header issues unless you demonstrate unauthorized access")

4. KNOWN ISSUES / DO-NOT-REPORT RULES
   - "We will not accept issues previously reported through other channels"
   - "Vulnerabilities in forked repos not eligible if present in upstream"
   - Explicit design decisions (e.g., "API token in Authorization header is by design")

5. REWARD TIERS PER TARGET
   - Map your finding to the correct tier (Database T1/T2, Website Console, Open Source, CTF)
   - Different targets have different reward ranges for same severity
```

**Finding triage before writing:** Assess each finding against program rules. Skip findings that:
- Violate explicit "do not report" rules
- Are by-design per the program's own documentation
- Are open-source default configs (e.g., default creds in Docker Compose)
- Would be duplicates of known issues in hacktivity/crowdstream

Write reports ONLY for findings that pass the 7-Question Gate AND align with program rules.

---

## THE MOST IMPORTANT RULE

> **Never use "could potentially" or "could be used to" or "may allow".**
> Either it does the thing or it doesn't. If you haven't proved it, don't claim it.

```
BAD:  "This vulnerability could potentially allow an attacker to access user data."
GOOD: "An attacker can access any user's order history by changing the user_id
       parameter to the target user's ID. I confirmed this using two test accounts:
       attacker@test.com (ID 123) successfully retrieved victim@test.com (ID 456)
       orders, including their shipping address and payment method last 4 digits."
```

---

## TITLE FORMULA

```
[Bug Class] in [Exact Endpoint/Feature] allows [attacker role] to [impact] [victim scope]
```

**Good titles (specific, impact-first):**
```
IDOR in /api/v2/invoices/{id} allows authenticated user to read any customer's invoice data
Missing auth on POST /api/admin/users allows unauthenticated attacker to create admin accounts
Stored XSS in profile bio field executes in admin panel — allows privilege escalation
SSRF via image import URL parameter reaches AWS EC2 metadata service
Race condition in coupon redemption allows same code to be used unlimited times
```

**Bad titles (vague, useless to triager):**
```
IDOR vulnerability found
Broken access control
XSS in user input
Security issue in API
Unauthorized access to user data
```

---

## HACKERONE REPORT TEMPLATE

```markdown
## Summary

[One paragraph: what the bug is, where it is, what an attacker can do. Be specific.
Include: endpoint, method, parameter, data exposed, required access level.]

Example: "The `/api/users/{user_id}/orders` endpoint does not verify that the
authenticated user owns the requested user_id. An attacker can enumerate any
user's order history, including PII (email, address, phone) and purchase history,
by incrementing the user_id parameter. No privileges beyond a standard free
account are required."

## Vulnerability Details

**Vulnerability Type:** IDOR / Broken Object Level Authorization
**CVSS 3.1 Score:** 6.5 (Medium) — AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N
**Affected Endpoint:** GET /api/users/{user_id}/orders

## Steps to Reproduce

**Environment:**
- Attacker account: attacker@test.com, user_id = 123
- Victim account: victim@test.com, user_id = 456
- Target: https://target.com

**Steps:**

1. Log in as attacker@test.com, obtain Bearer token

2. Send the following request:

```
GET /api/users/456/orders HTTP/1.1
Host: target.com
Authorization: Bearer ATTACKER_TOKEN_HERE
```

3. Observe response:

```json
{
  "orders": [
    {"id": 789, "items": [...], "email": "victim@test.com", "address": "123 Main St..."}
  ]
}
```

The response contains victim's full order history and PII despite being requested
by a different user.

## Impact

An authenticated attacker can enumerate all user orders by iterating user_id values.
This exposes: full name, email, shipping address, purchase history, and payment
method (last 4). With ~100K users, this represents a mass PII breach affecting
all registered users. Exploitation requires only a free account and takes minutes
with a simple loop.

## Recommended Fix

Add server-side ownership verification:
```python
if order.user_id != current_user.id:
    raise Forbidden()
```

## Supporting Materials

[Screenshot showing attacker's session returning victim's order data]
[Video walkthrough if available]
```

---

## BUGCROWD REPORT TEMPLATE

```markdown
# [IDOR] User order history accessible without authorization via /api/users/{id}/orders

**VRT Category:** Broken Access Control > IDOR > P2

## Description

[Same impact-first paragraph as HackerOne summary]

## Steps to Reproduce

[Same structured steps — exact HTTP requests, exact responses]

## Proof of Concept

[Screenshot/video showing the actual impact]

## Expected vs Actual Behavior

**Expected:** 403 Forbidden when user_id does not match authenticated user
**Actual:** 200 OK with victim's full order data

## Severity Justification

P2 (High) — Direct read access to other users' PII. Affects all user accounts.
No user interaction required. Exploitable by any authenticated user.
Automated enumeration could exfil all [N] user records in minutes.

## Remediation

Add ownership verification: `if order.user_id != current_user.id: raise 403`
```

---

## INTIGRITI REPORT TEMPLATE

```markdown
# [Bug Class]: [Exact Impact] in [Endpoint/Feature]

## Description

[Impact-first paragraph. Start with what an attacker can do, not with how you found it.
Include: endpoint, method, parameter, data exposed, required privileges.]

## Steps to Reproduce

**Environment:**
- Attacker: email=attacker@test.com (standard account, no special role)
- Victim: email=victim@test.com
- Tested: [date]

**Reproduction steps:**

1. [Login as attacker / visit URL / send request]

2. Send the following HTTP request:

\```http
METHOD /endpoint HTTP/1.1
Host: target.com
Authorization: Bearer ATTACKER_TOKEN
Content-Type: application/json

{"param": "victim_id_here"}
\```

3. Observe response contains victim's private data:

\```json
{"email": "victim@test.com", "address": "123 Main St", ...}
\```

## Impact

[Specific, quantified impact. What data, how many users, what can attacker do.]

CVSS 3.1 Score: X.X ([Severity]) — AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N

## Remediation

[1-3 sentence concrete fix. Include code if helpful.]

## Attachments

[Screenshot or Loom video showing the impact — Intigriti triagers prefer video for complex bugs]
```

**Intigriti-specific notes:**
- Title format: `[Bug Class]: [One-line impact]` (no formula required, but keep it specific)
- Severity is set by you: Critical/High/Medium/Low/Exceptional
- CVSS 3.1 is standard (CVSS 4.0 also accepted on newer programs)
- PoC video is valued much more than screenshot alone — record with Loom
- Safe harbor: Intigriti enforces it, be comfortable going slightly aggressive with testing

---

## IMMUNEFI REPORT TEMPLATE

```markdown
# [Bug Class] — [Protocol Name] — [Severity]

## Summary

[One paragraph with: root cause, affected function, economic impact, attack cost.
Include numbers where possible: "attacker can drain $X in Y transactions."]

## Vulnerability Details

**Contract:** `VulnerableContract.sol`
**Function:** `claimRedemption()`
**Bug Class:** Accounting State Desynchronization
**Severity:** Critical

### Root Cause

[Exact code snippet showing the vulnerable code with comments]

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
// Foundry PoC — run: forge test --match-test test_exploit -vvvv

contract ExploitTest is Test {
    // ... full working exploit
}
```

## Impact

[Quantified: "Attacker can drain X% of TVL = $Y at current rates.
Requires $Z gas. Attack is repeatable."]

## Recommended Fix

[Specific code change with before/after]
```

---

## CVSS 3.1 QUICK SCORING

### Formula
```
CVSS = f(AV, AC, PR, UI, S, C, I, A)
```

### Metric Quick Picks

| Metric | Value | Weight | When |
|---|---|---|---|
| **Attack Vector (AV)** | Network | +0.85 | Via internet |
| | Local | +0.55 | Local access needed |
| **Attack Complexity (AC)** | Low | +0.77 | Repeatable |
| | High | +0.44 | Race/timing needed |
| **Privileges Required (PR)** | None | +0.85 | No login |
| | Low | +0.62 | Regular user account |
| | High | +0.27 | Admin account |
| **User Interaction (UI)** | None | +0.85 | No victim action |
| | Required | +0.62 | Victim must click |
| **Scope (S)** | Changed | higher | Affects browser/OS/other |
| | Unchanged | lower | Stays in app |
| **Confidentiality (C)** | High | +0.56 | All data exposed |
| | Low | +0.22 | Limited data |
| **Integrity (I)** | High | +0.56 | Can modify any data |
| **Availability (A)** | High | +0.56 | Crashes service |

### Typical Scores by Bug Class

| Bug | Typical CVSS | Severity |
|---|---|---|
| IDOR (read PII) | 6.5 | Medium |
| IDOR (write/delete) | 7.5 | High |
| Auth bypass → admin | 9.8 | Critical |
| Stored XSS (any user) | 5.4–8.8 | Med–High |
| SQLi (data exfil) | 8.6 | High |
| SSRF (cloud metadata) | 9.1 | Critical |
| Race condition (double spend) | 7.5 | High |
| GraphQL auth bypass | 8.7 | High |
| JWT none algorithm | 9.1 | Critical |

---

## SEVERITY DECISION GUIDE

### Critical (P1)
- Full account takeover of any user without interaction
- Remote code execution
- SQLi with ability to dump/modify entire DB
- Auth bypass to admin panel
- SSRF to cloud metadata → IAM credentials exfil

### High (P2)
- Mass PII exposure (email, phone, SSN, payment data)
- Privilege escalation from user to admin
- SSRF reaching internal services (data returned)
- Stored XSS executing for all users of sensitive feature
- Payment bypass / financial loss without limit

### Medium (P3)
- IDOR on specific user's non-critical data
- XSS on low-sensitivity page requiring victim interaction
- CSRF on important but non-critical action
- Rate limit bypass on OTP (with effort demonstrated)

### Low (P4)
- Information disclosure (non-sensitive, no PII)
- Clickjacking on sensitive action WITH working PoC
- CORS on limited data

---

## SEVERITY SELF-ASSESSMENT

Each YES raises severity:
```
1. Exposes PII / health / financial data of other users?        → +1 severity
2. Allows account takeover or privilege escalation?             → +2 severity
3. Requires ZERO user interaction from victim?                  → +1 severity
4. Affects ALL users (not specific condition)?                  → +1 severity
5. Remotely exploitable with no internal network access?        → baseline for High+
```

---

## DOWNGRADE COUNTERS

| Program Says | Counter With |
|---|---|
| "Requires authentication" | "Attacker needs only a free account — no special role or permission" |
| "Limited impact" | "Affects [N] users / exposes [PII type] / $[amount] at risk" |
| "Already known" | "Show me the report number — I searched hacktivity and found none" |
| "By design" | "Show me the documentation stating this is intended behavior" |
| "Low CVSS" | "CVSS doesn't capture business impact — attacker can extract [X] in [Y] minutes" |
| "Not exploitable" | "Here is the exact response showing victim's data returned to attacker session" |

---

## THE 60-SECOND PRE-SUBMIT CHECKLIST

```
[ ] Title follows formula: [Class] in [endpoint] allows [actor] to [impact]
[ ] First sentence states exact impact in plain English
[ ] Steps to Reproduce has exact HTTP request (copy-paste ready)
[ ] Response showing the bug is included (screenshot or JSON body)
[ ] Two test accounts used — not just one account testing itself
[ ] CVSS score calculated and included
[ ] Recommended fix is 1-2 sentences (not a lecture)
[ ] No typos in endpoint paths or parameter names
[ ] Report is < 600 words — triagers skim long reports
[ ] Severity claimed matches impact described — don't overclaim
[ ] Never used "could potentially" or "may allow"
[ ] PoC is reproducible by triager from a fresh state
```

---

## CVSS 4.0 QUICK REFERENCE (newer programs)

CVSS 4.0 replaced CVSS 3.1 in November 2023. Some newer programs require it.

### Key Differences from CVSS 3.1

| Metric | CVSS 3.1 | CVSS 4.0 |
|---|---|---|
| Attack Vector | Network/Adjacent/Local/Physical | Same |
| Attack Complexity | Low/High | Low/High |
| **NEW**: Attack Requirements | (didn't exist) | None/Present (replaces some PR/UI) |
| Privileges Required | None/Low/High | Same |
| User Interaction | None/Required | None/Passive/Active |
| Scope | Unchanged/Changed | REMOVED |
| **NEW**: Sub-Impact metrics | (didn't exist) | Vulnerable/Subsequent system impact |

### CVSS 4.0 Score Examples

| Finding | CVSS 4.0 Score | Vector |
|---|---|---|
| Unauthenticated RCE | 10.0 | CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H |
| IDOR read PII, auth required | 6.9 | CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N |
| Stored XSS, admin views it | 8.2 | CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N |
| SSRF → cloud metadata | 8.7 | CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:N |

### Quick CVSS 4.0 Calculator
```
Use: https://www.first.org/cvss/calculator/4.0
Key fields:
  VC/VI/VA = Vulnerable System Confidentiality/Integrity/Availability
  SC/SI/SA = Subsequent System (downstream impact)
  AT = None (no special condition) | Present (race/specific config needed)
  UI = None | Passive (victim visits URL) | Active (victim takes explicit action)
```

**Practical rule**: If program uses CVSS 4.0 and you don't know the vector, use the calculator and include the full string starting with `CVSS:4.0/AV:...`. Programs cannot dispute a valid vector string.

---

## HUMAN TONE GUIDELINES

**Write to a person, not a system:**
- Triagers are tired. Get to the impact in sentence 1.
- Use "I" not "the researcher" — you found it, own it
- Short paragraphs, bullet points for steps
- Hyperlink relevant docs if needed

**Escalation language (when payout is being downgraded):**
```
"This vulnerability does not require any special privileges — only a free account."
"The exposed data includes [PII type], which is subject to GDPR requirements."
"An attacker can automate this with a simple loop — all [N] records in minutes."
"This is exploitable externally without network access to any internal system."
"The impact is equivalent to a full data breach of [feature/data type]."
```

**Avoid:**
- Jargon the triager might not know
- 5-paragraph explanations of what IDOR is (they know)
- Theoretical chains ("could be combined with X to...")
- Passive voice ("it was observed that...")
- Qualifying language ("seems to," "appears to")

---

## STEPS TO REPRODUCE FORMAT (triager-optimized)

```markdown
**Setup:**
- Account A (attacker): email=attacker@test.com, ID=111
- Account B (victim): email=victim@test.com, ID=222
- Both created via normal registration — no special access

**Steps:**

1. Log in as Account A
2. Send this request (replace `111` with victim ID `222`):

\```
GET /api/v2/resource/222 HTTP/1.1
Host: target.com
Authorization: Bearer ACCOUNT_A_TOKEN
\```

3. Response contains Account B's private data:

\```json
{"id": 222, "email": "victim@test.com", "name": "Victim User", "address": "..."}
\```

**Expected:** 403 Forbidden
**Actual:** 200 OK with victim's private data
```

---

### Bugcrowd — User's Preferred Format (eToro Gold Standard)

When writing Bugcrowd reports for this user, follow the eToro MCP server report structure. The user writes better reports than the agent — this is the MINIMUM quality standard.

**Structure:**
```
## Description
[Summary paragraph — what, where, why it matters]

[Exposure breakdown by CATEGORY with bold headers and bullet lists]

## Business Impact
[Specific attack capabilities enabled, effort reduction, chain potential]

## Steps to Reproduce
[Numbered steps, each with curl command + expected response]

## Proof of Concept
[List what screenshots should show: (1), (2), (3)]

## Remediation
[Numbered, specific, actionable fixes]
```

**CRITICAL: Deliver as ONE continuous text block.** User gets EXTREMELY frustrated ("biar 1x copy anjing") when given sectioned drafts requiring manual assembly. The ENTIRE description goes in one block — no "paste this here, then paste there."

**NEVER offer multiple draft options.** Pick the best format on first try. User doesn't want to choose or iterate on formatting.

**NEVER show code blocks in chat.** Run tools silently. The user has corrected this 5+ times in one session. Code blocks in Telegram = spam. Exception: code blocks are OK when explicitly requested (e.g., "buatkan script"), but for Bugcrowd report drafts, deliver the text as plain text, not in a code block.

---

## POST-REPORT BOUNTY NEGOTIATION + INVOICE WORKFLOW

Use this when a project acknowledges a report but payout is informal, discretionary, or handled by finance.

### Tone for follow-up DMs
Keep it calm, short, and non-needy. Do not over-negotiate after silence. If the team has not replied for ~3 days after a bounty/payment discussion, send one closing follow-up with payment details framed as optional/discretionary.

**Discretionary reward follow-up template:**

```markdown
Hi team,

Just following up once more on this.

I understand if the finding is considered outside the formal bounty scope, but I hope the report was still useful for improving your security posture.

If the team is open to a discretionary reward or token gesture, you can send it here:

[CHAIN]: [PAYMENT_ADDRESS]

No pressure either way — I appreciate the time and review.

Best regards,
[NAME]
```

**Follow-up rules (STRICT):**
- ❌ NEVER use "no rush" — user explicitly hates this passive phrase
- ❌ Don't be desperate or reveal financial urgency
- ✅ Short and direct: "Hey @Name, any update on the payment?"
- ✅ Warm but not over-explaining
- ✅ If multiple days passed, mention timeframe casually: "from last week"

**If they ask for payment method casually:**

```markdown
Hi [Name], thanks a lot 🙏

Crypto works best for me if possible.

[CHAIN]:
[PAYMENT_ADDRESS]

If you still need an invoice, I can make one too.
```

### Invoice meaning and fields
An invoice is a one-page admin document for the team/finance department. Keep it simple — not tax-heavy unless they ask.

Required fields:
- Invoice number: `INV-[PROJECT]-YYYYMMDD`
- Date and payment due: “Upon receipt”
- From: researcher name + email
- Bill To: project/company + Security / Finance Team
- Description: “Security research and responsible vulnerability disclosure reward for [Project].”
- Amount: agreed USD/USDC amount
- Tax: `$0.00` unless user says otherwise
- Payment method: chain + wallet address
- Footer: “This invoice is issued for a discretionary security research / vulnerability disclosure reward. Please confirm once payment has been sent.”

### Filename convention
Use a professional filename without exposing the amount unless user asks:

`[Researcher_Name]_[Project]_Invoice.pdf`

Example: `Khasbi_Maulana_OnRe_Invoice.pdf`

### Invoice template artifact

A reusable HTML template is available at `templates/security-reward-invoice.html`. Copy it, replace placeholders, render to PDF, and name the file using the filename convention above.

### Delivery caption

```markdown
Hi [Name], here’s the invoice for the security research reward.

Payment address is included in the invoice as well.

Thank you.
```

### Safety checks before sending
- Verify wallet address and chain match the project/payment method.
- Do not include private keys, seed phrases, or internal notes.
- If sending a PDF, use a clean filename; avoid raw temp names like `invoice.pdf` or names with internal paths.
- If the user wants casual DM tone, avoid overly formal “Dear Sir/Madam” language.

---

## Related Skills & Chains

- **`triage-validation`** — When deciding whether to write a report at all. Workflow primitive: NEVER open this skill before `triage-validation`'s 7-Question Gate passes; a finding that fails the gate should be killed, not written up.
- **`bugcrowd-reporting`** — When the target is a Bugcrowd program. Workflow primitive: this skill's body template is the foundation; `bugcrowd-reporting` overlays VRT selection, severity-request paragraph, OOS-clause rebuttals on top.
- **`evidence-hygiene`** — When PoC screenshots / HARs are being attached to the report. Workflow primitive: every artifact referenced in the "Supporting Materials" / "Proof of Concept" section gets routed through `evidence-hygiene` for cookie + PII redaction before attachment.
- **`redteam-report-template`** — When the engagement is an external red team (NOT bug bounty). Workflow primitive: confirm engagement mode via `bb-methodology` PART 0; if red-team, swap this skill out for `redteam-report-template` (different audience, different structure: Subject / Observations / Description / Impact / Recommendation / PoC).

## Reference Files
- `references/aiven-bugcrowd-program-rules.md` — Aiven Managed Bug Bounty program rules, reward tiers, scope, submission requirements, special rules, and VRT exclusions. Use as template for documenting other programs.
- `references/origin-protocol-strapi-key-case-study.md` — SSR stream data key exposure case study. Strapi API key leaked in React Router SSR HTML on `originprotocol.com`. Immunefi Web/App Critical ($25K). Pattern: heavy SC audit coverage doesn't protect web surface.

---

## Operator Notes (Claude-BugHunter)

> Engagement-derived + 2026-specific additions to the vendored foundation.

### Format: 1x Copy-Paste (June 2026)

User wants ONE continuous text block for the Description field on Bugcrowd/Immunefi. NO markdown headers (##), NO sections separated by headers. Just plain text paragraphs with line breaks. Use section labels as bold inline text or plain text labels.

### Google Docs-ready format (July 2026 — for Superteam, Google Doc link submissions)

When the submission requires a Google Docs link (not a platform text field), use this format:

- No markdown syntax AT ALL — no ## headers, no ``` code fences, no * bullets that might not render
- Section dividers: single `=` on its own line (renders cleanly in Docs, easy to replace with horizontal rules)
- Bold texts: use section labels like **Finding 1 — Title** but format as plain readable text since Docs supports paste of bold
- Curl commands: inline or indented, NOT inside code fences
- Steps: numbered with just numbers (1. 2. 3.) — Docs auto-formats lists
- Keep it concise: finding, steps, evidence, impact, fix — no more than 500 words per finding
- Focus on 1-2 strongest findings first, add weaker ones after

This is DIFFERENT from the Bugcrowd "1x Copy" format — this one must render cleanly when pasted into a Google Doc and shared as a link.

**WRONG (user hated this):**
```
## Description
Text here.

## Business Impact
Text here.
```

**RIGHT (user approved — eToro MCP report gold standard):**
```
The Model Context Protocol (MCP) server at https://mcp.public-api.etoro.com/ is live and completely unauthenticated...

Business Impact

An unauthenticated attacker obtains a complete map of the entire eToro Public API...

Steps to Reproduce

1. Initialize an MCP session (no authentication):
   POST https://mcp.public-api.etoro.com/
```

### VRT Category Check (June 2026)
Always check VRT severity BEFORE writing full report:
- OAuth client secret in JS → `Sensitive Data Exposure > Sensitive Data Hardcoded > OAuth Secret` = P5/Informational ($0) — NOT worth submitting
- Source maps exposed → `Sensitive Data Exposure > Disclosure of Secrets > For Internal Asset` = P3 ($600-$850) — worth submitting
- Don't waste time writing reports for P5/Informational findings

### Evidence Screenshots (June 2026)
Generate clean terminal-style screenshots using PIL:
- Dark background (30,30,30), colored text by category
- HTTP 200 responses in green, file sizes in yellow, paths in cyan
- ZIP all screenshots + PoC script for Bugcrowd attachment upload
- File at: /root/aiven-bugcrowd-reports/ (reference implementation)
> authorized engagements + Phase 2 verification across this repo's 31+
> skill-area live tests. The upstream methodology covers the WHAT; this
> layer covers the WHEN-IT-ACTUALLY-WORKS and the FAILURE-MODES.

### Title formula in practice

`<asset> | <bug class> | <impact>` — three components, no fluff. Triagers read titles in roughly three seconds and use them to order the queue.

- BAD: "Interesting finding on /api/users"
- BAD: "IDOR vulnerability in API"
- GOOD: "Authenticated IDOR on /api/users/{uid} -> admin email + role disclosure"
- GOOD: "Unauthenticated SSRF on /preview?url= -> AWS metadata 169.254.169.254 reachable"

The bad titles get opened last. The good titles get opened first. Same finding, different queue position, different triage day, different payout speed.

### What triagers actually read

Their reading sequence on a fresh report:

1. **Title** (3 seconds)
2. **First paragraph of impact / summary** (15 seconds)
3. **The curl command or HTTP request block** (30 seconds)
4. **Reproduction steps** (only if the first three were convincing)
5. **Everything else** (only on follow-up review)

Optimize the top of the report ruthlessly. Save narrative for the middle. Triagers who are convinced by step 3 will rubber-stamp the rest; triagers who aren't convinced by step 3 won't read step 5.

### CVSS 3.1 vs Bugcrowd VRT vs H1 default severity

These three systems disagree about 30% of the time. The most common gap: a finding that scores CVSS 7.x (High) maps to Bugcrowd P4 (Low) or H1 Medium-default. When the platform default rates lower than CVSS:

1. **File the severity-request paragraph as the first body section.** Bugcrowd respects this. (See `bugcrowd-reporting` for the canonical template.)
2. **Anchor the request in CVSS vector string + business impact, not feelings.** "CVSS 3.1 AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N = 7.5 High because Confidentiality:High applies to cross-tenant data exposure."
3. **Cite the platform's own VRT entry** that matches your finding. Don't argue against the platform; route within it.

An authorized bug-bounty engagement saw P4-default findings escalated to P3 via the severity-request paragraph. The escalation isn't automatic — you have to ask, with grounded reasoning, in the first body section.

### PoC redaction discipline

ALWAYS redact personal information from PoC responses before including in reports:

- Replace real names with "Test User" or "Researcher"
- Replace real emails with the program's test email (e.g., researcher@bugcrowdninja.com)
- Replace real project names with "test-project" or generic names
- Replace real API tokens with `[TEST_TOKEN]` or `[VICTIM_TOKEN]` placeholders
- Keep the JSON structure intact — just replace the sensitive values

**Why:** Reports are logged forever on the platform. Real PII in reports creates compliance issues and looks unprofessional.

### Program-specific finding patterns

**CORS with Authorization header (no Access-Control-Allow-Credentials):**
- When ACAO reflects origin but `Access-Control-Allow-Credentials` is NOT set, cookies are not sent cross-origin
- BUT if `Authorization` is in ACAH, the preflight passes and authenticated requests work (token in header, not cookie)
- Impact: requires attacker to already possess the token (via XSS/phishing/token leak)
- Severity: P3 Medium (not P2) unless you can demonstrate token theft chain
- Triager will ask "how does attacker get the token?" — answer this in the report

**OAuth client secret in public JavaScript:**
- Always report — programs explicitly encourage credential reports ("we will determine scope")
- Even if token exchange returns `invalid_client` (rotated/dead), the leak is still valid
- Include: exact URL of JS file, exact credential values, what else is leaked (Sentry DSN, internal URLs)
- Severity: P2 High (CWE-798)

**Clickjacking on internal admin tools:**
- Check program's specific clickjacking policy FIRST — some programs say "do not report cookie/header issues unless you demonstrate unauthorized access"
- If program has this policy: must show actual unauthorized action, not just iframe loading
- If program doesn't have this policy: iframe loading + admin tool = P2/P3
- Always include: missing headers list, PoC HTML, what admin actions could be triggered

**Token/session expiration without confirmation:**
- Endpoint that immediately expires ALL tokens with single request = valid DoS
- Chain with token theft for full impact
- Missing: confirmation dialog, secondary auth, notification email, rate limiting
- Severity: P3 Medium (requires pre-compromise)

**Health endpoints on internal APIs:**
- Most programs reject as "standard practice" — skip unless program explicitly accepts
- If admin API URL is not publicly documented, the URL disclosure may be more valuable than the health check itself

### Deep scan report structure

When performing comprehensive scans across multiple attack surfaces, organize findings in a structured report:

```
# SCAN COVERAGE (table: Phase | Area | Status)
# FINDINGS (numbered by severity: P2-001, P2-002, P3-001...)
# NOT EXPLOITABLE (table: Finding | Why Not)
# SERVICES CREATED (for testing reference)
# SUMMARY (table: Severity | Count | Findings)
```

Each finding should include: Target, CVSS, CWE, Description, PoC, Impact, Remediation.
"NOT EXPLOITABLE" section shows thoroughness — you tested things that didn't work, which builds credibility.

### Evidence rotation

Everything in the submission body is logged forever by the platform. Operate accordingly:

- Use throwaway test accounts created specifically for the engagement.
- Rotate cookies / tokens after each submission (don't reuse the cookie that's pasted in the report).
- Never paste production cookies, real user emails, or real PII into the report body — redact in the PoC step.
- Screenshots of admin panels: blur the user list, blur the URL bar if it contains tokens.

Cross-link `evidence-hygiene` for the full capture-and-redact protocol.

### Templates by platform — when they differ

| Platform | Tone | Required Structure | Severity Mechanism |
|---|---|---|---|
| HackerOne | Narrative | Summary -> Steps -> Impact -> Suggested fix | Triager-set, contestable |
| Bugcrowd | Structured | Severity request -> VRT category -> Title -> Body -> Remediation | VRT-default + manual override paragraph |
| Intigriti | Between | Summary -> PoC -> Impact -> Recommendation | Researcher-proposed, triager-confirmed |
| Immunefi | PoC-first | Working PoC code -> Walkthrough -> Impact -> Severity | Foundry/Hardhat code is the primary deliverable |

Picking the wrong template style costs validity. A narrative-heavy Bugcrowd report misses the VRT mapping the triager needs; a structured H1 report reads as terse and gets follow-up questions that delay payout.

### The single biggest report-writing mistake

Claiming an attack works "in theory" or "could be chained to [bigger impact]" without demonstrating it. Triage-validation Q6 (impact beyond technically possible) kills these on the validation side; report-writing has to mirror it on the writing side.

Two valid paths:

1. **Show concrete impact end-to-end.** Capture the chain on a test account. Paste the full request/response sequence. Done.
2. **Downgrade the severity claim to match what you actually demonstrated.** "IDOR on /api/users/{uid} reading email + role" is real and reportable; "IDOR chained to potential admin takeover" is not until you demonstrate the takeover.

Pick one. Never split the difference with "could potentially" or "may allow" — those phrases are the triager's signal that the report is theoretical, and theoretical reports get N/A.
- **`bb-methodology`** — When Phase 5's report-writing step starts. Workflow primitive: Phase 5 calls `/report` which loads this skill for the platform-specific template (H1 / Bugcrowd / Intigriti / Immunefi).
