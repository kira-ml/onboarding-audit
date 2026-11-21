# Privacy and Data Handling

**Status:** V1 policy, 2026-11-21.
**Scope:** The open-source repository and any evaluation extract used with it.

---

## 1. Default rule

The repository uses **public or synthetic data only**. The examples, the demo
log, and the pilot frame contain no real customer data.

Do not put a bank's production log, raw documents, names, account numbers, or
unhashed contact data in this repository.

## 2. If you use a real log

A real evaluation extract must:

- be pseudonymized; identifiers hashed or replaced with stable keys;
- contain only the fields needed for the evaluation (data minimization);
- exclude raw documents, names, account numbers, and unhashed contact data;
- be stored in a controlled, access-limited location;
- be covered by a data-sharing agreement and, where required, a data processing
  agreement;
- follow the Data Privacy Act (RA 10173), NPC Advisory 2024-04, NPC Circular
  2022-04, and BSP Circular 1170/1213 obligations that apply to the institution;
- have a defined retention period and deletion process.

## 3. Recommended fields

Use `application_id` as a stable, non-PII key. Use `*_hash` fields for device,
phone, and email. Do not use a raw customer identifier as the join key.

The schema is in [`SCHEMA.md`](SCHEMA.md); the data card is in
[`DATA.md`](DATA.md).

## 4. Sandbox and read-only use

A pilot should run in a read-only sandbox:

- no production write access;
- no automated approval/rejection changes;
- no customer contact;
- no raw PII in the evaluation extract;
- access limited to the named analyst and reviewer.

## 5. Audit trail

Record:

- who ran the report;
- the log version/hash;
- the config and cost matrix;
- the gate result and the memo;
- the reviewer and decision.

The memo and JSON are the evaluation record; do not hand-edit them.

## 6. Incident rule

If a real log or PII is accidentally committed or shared:

1. Stop using the repository.
2. Remove the data from the working tree and history.
3. Notify the data owner and the institution's privacy office.
4. Follow the institution's incident process.

Do not post the data in an issue, a pull request, or a chat.

## 7. What this project does not do

- It does not anonymize a raw production log.
- It does not provide legal advice or a privacy impact assessment.
- It does not replace the institution's data-governance process.

## 8. Related documents

- Schema: [`SCHEMA.md`](SCHEMA.md)
- Data card: [`DATA.md`](DATA.md)
- Audit design: [`AUDIT_DESIGN.md`](AUDIT_DESIGN.md)
- BSP/AFASA/NPC mapping: [`BSP_MAPPING.md`](BSP_MAPPING.md)
- Report usage: [`REPORT_USAGE.md`](REPORT_USAGE.md)
