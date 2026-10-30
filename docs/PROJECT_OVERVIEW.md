# GradeLens: Project Overview & Scope

## 1. Executive Summary
**GradeLens** is an academic performance analytics and weakness detection platform engineered to solve the "blind mark syndrome" in higher education. While traditional learning management systems only record coarse aggregate percentages, GradeLens analyzes academic outcomes at the atomic question level, linking errors to curriculum topics, cognitive mistake types, and subsequent revision activities.

## 2. Target Stakeholders & Use Cases

### A. Students
- **Understand Concept Deficits**: Discover exactly which topics cause repeated mark deductions rather than guessing.
- **Root-Cause Error Diagnostics**: Distinguish between conceptual gaps, formula slips, calculation errors, and time-management issues.
- **Track Revision ROI**: Measure whether spending 90 minutes studying a topic translated to score improvement on the next examination.
- **Daily Focus**: Maintain daily revision tasks and weekly milestone goals.

### B. Faculty & Course Instructors
- **Early At-Risk Detection**: Flag struggling students transparently well before semester finals.
- **Curriculum Calibration**: Identify difficult topics across the cohort to adjust lecture pacing and homework assignments.
- **Assessment Quality**: Spot poorly calibrated questions (e.g. questions where 90% of students lose marks).

## 3. Scope Boundaries & Assumptions
- **Transparent Heuristics over Black-Box ML**: Recommendations and weakness classifications use deterministic mathematical rules rather than unexplainable black-box models.
- **Zero Paid APIs**: No reliance on external commercial LLMs or cloud endpoints; runs completely offline and locally.
- **Dual Database Architecture**: Native PostgreSQL 18 production target with zero-setup SQLite engine for friction-free local execution and testing.
