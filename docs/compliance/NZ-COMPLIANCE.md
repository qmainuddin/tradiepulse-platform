# New Zealand Tradesperson Compliance & Regulatory Guide

TradiePulse connects customers to tradespeople who perform safety-critical work across New Zealand. Verification is a critical legal and safety surface. The TradiePulse verification engine uses a pluggable `VerificationProvider` architecture allowing rules to be updated via configuration rather than system redesigns.

---

## 1. Trade-Specific Regulatory Boards

### 1.1 Electricians: Electrical Workers Registration Board (EWRB)
- **Governing Body:** Electrical Workers Registration Board under the Electricity Act 1992.
- **Licence Requirements:**
  - Registered Electrician, Electrical Inspector, or Electrical Engineer.
  - Must possess a **current practising licence** (renewed every 2 years with competence programme compliance).
- **Verification Provider Seam (`EWRBVerificationProvider`):**
  - Validates registration number and current practising licence status against the public register.
  - Checks for active disciplinary suspensions or restrictions.

### 1.2 Plumbers, Gasfitters & Drainlayers (PGDB)
- **Governing Body:** Plumbers, Gasfitters and Drainlayers Board under the Plumbers, Gasfitters, and Drainlayers Act 2006.
- **Licence Requirements:**
  - Certifying Plumber/Gasfitter/Drainlayer (can work independently and supervise).
  - Licensed Plumber/Gasfitter/Drainlayer (works under supervision of a Certifying tradesperson).
- **Verification Provider Seam (`PGDBVerificationProvider`):**
  - Confirms registration class, active annual licence, and authorization to sign off work.

### 1.3 Automotive Mechanics
- **Governing Body:** No mandatory national licensing board for general mechanics in NZ.
- **Qualification Requirements:**
  - NZ Certificate in Light Automotive Engineering (NZQA Level 4) or trade equivalent.
  - Warrant of Fitness (WoF) vehicle inspector authority (if vehicle inspection services are offered) via Waka Kotahi NZTA.
- **Verification Provider Seam (`MechanicQualificationProvider`):**
  - Verified trade certificates and proof of trade insurance.

---

## 2. Tax & Inland Revenue (IRD) Compliance

- **IRD Number Collection:**
  - Validated via standard NZ 8 or 9 digit modulus 11 checksum algorithm.
  - Handled in test/sandbox by `MockIRDProvider` and routed to secure IRD gateway in production.
- **GST Obligations:**
  - Tradespersons earning over NZD \$60,000 gross per annum must provide active GST registration numbers.
- **Storage:** IRD numbers are encrypted at rest using AES-256-GCM.

---

## 3. Identity, Safety & Insurance

- **Identity Verification:** Government-issued photo ID (NZ Passport / NZ Driver Licence / RealMe).
- **Public Liability Insurance:** Mandatory minimum NZD \$2,000,000 public liability cover certificate with active policy dates.
- **Criminal History / Police Vetting:** Background checks required for in-home residential service providers.

---

## 4. Christchurch & Canterbury Regional Regulations

- **Post-Earthquake Building Standard Compliance:**
  - High-risk building repairs and drainage require compliance with Christchurch City Council (CCC) consenting frameworks and Canterbury Regional Council (Environment Canterbury) water regulations.
- **Regional Gating (`RegionalComplianceProvider`):**
  - Trades operating within the Christchurch/Canterbury coordinates boundary (approx Lat -43.53, Lng 172.63) trigger regional insurance and consent awareness verification steps.

---

## 5. NZ Privacy Act 2020 Compliance

- **Information Privacy Principles (IPPs):**
  - PII minimisation: Collect only data necessary for identity and job execution.
  - Storage & Security: Encryption at rest and in transit. Strict role-based access control.
  - PII Redaction: LLM pipelines automatically scrub customer and tradie phone numbers, emails, and IRD numbers before prompt dispatch.
  - Mandatory Breach Notification: Architecture supports real-time audit logging and alerting for privileged data access or impersonation events.
