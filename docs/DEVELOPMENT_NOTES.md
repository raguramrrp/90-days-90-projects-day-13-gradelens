# GradeLens: Engineering Decisions & Development Notes

## 1. Design Decisions & Trade-Offs

### A. Dual-Engine Architecture (PostgreSQL 18 Target + SQLite Local Engine)
- **Problem**: In restricted developer sandboxes, continuous integration pipelines, and non-admin laptops, the Windows PostgreSQL service may not always be started, or permissions may prevent running `net start postgresql-x64-18`.
- **Solution**: GradeLens implements a unified database interface. By default, it targets PostgreSQL, but if PostgreSQL is unavailable or if `DATABASE_TYPE=sqlite` is specified in `.env`, it provides transparent diagnostics and runs with an embedded SQLite engine. Both engines share identical schema DDL, constraints, and views.

### B. Deterministic Weakness Classification vs. Deep Learning
- **Decision**: Rejecting black-box ML for weakness classification.
- **Rationale**: In academic intelligence, explainability and transparency are paramount. A student or faculty member must understand *why* a topic was flagged. The rule-based engine provides clear mathematical thresholds ($\ge 75\%$ for Strong, $<60\%$ across $\ge 2$ exams for Repeated Weakness) accompanied by the exact evidence chain.

### C. Scientific Framing of Revision Effectiveness
- **Decision**: Avoiding claims of causal proof.
- **Rationale**: An increase in score from 40% to 90% following a revision session is an *observed comparison*. Exam question difficulty, question type, or time constraints can also influence the outcome. GradeLens transparently annotates all effectiveness cards with this caveat.

### D. Multi-Tier Import Validation
- **Decision**: Validating imports row-by-row before database execution.
- **Rationale**: Dirty academic datasets often have negative marks, marks exceeding maximum values, or misspelled categories. GradeLens isolates invalid rows into a downloadable error CSV, while allowing valid rows to be committed atomically within a transaction.
