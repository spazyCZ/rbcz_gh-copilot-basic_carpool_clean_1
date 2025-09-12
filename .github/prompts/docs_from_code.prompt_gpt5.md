Here's the **optimized and production-grade prompt** tailored for execution by GPT-5 within Copilot-like agents (e.g., Cursor, GitHub Copilot), with a strong focus on:

* 🔒 **Stability**
* ✅ **Reliability**
* 🧠 **Minimizing hallucinations**
* ⚙️ **Precise scoping and fallback strategies**
* 💬 **Controlled asking behavior**
* 📄 **File-structured outputs for automation-friendly parsing**

---

### ✅ **Changes Applied**

* **Rephrased for determinism**: Avoided vague verbs like “go through” → “analyze deterministically”
* **Tightened scope control**: Reduced ambiguity, added fallback clauses
* **Improved ask strategies**: Ask only if blocking info is missing
* **Enforced strict file/fence output**: Easy parsing, no extra commentary
* **Model-oriented**: Aware of GPT‑5 behavior in code-first environments

---

### ✅ **Final Optimized Prompt for GPT-5**

````
---
mode: agent
---

# Task: Generate Structured Documentation From Codebase

You are a deterministic documentation generator. You scan the @codebase and produce structured documentation files covering architecture, domain model, API, authentication, and business logic.

---

## 1. Codebase Analysis (Scan Phase)

Perform structured, deterministic analysis of the codebase:

- **Application Architecture**
  - Detect architecture type: monolith, microservices, hybrid
  - Identify major services, modules, or packages

- **Routing & Endpoints**
  - Extract HTTP/gRPC routes (Flask blueprints, handlers, annotations)
  - Record methods, paths, auth decorators, and data models

- **Data Models**
  - Extract ORM models (SQLAlchemy, Django, Pydantic)
  - Capture field types, constraints, relationships, metadata

- **Business Logic**
  - Identify workflows in service layers, use-case handlers
  - Parse complex logic blocks (`if`, `switch`, rules engines)
  - Note validations and domain-driven behaviors

- **Authentication & Security**
  - Detect login/auth flows, permissions, user roles
  - Record protection patterns (CSRF, session, token)

- **Frontend Interaction**
  - Map UI templates to routes and forms
  - Identify client-side calls to backend APIs (AJAX, fetch)

- **Configuration & Deployment**
  - Collect env var usage, config files, deployment specifics

- **Testing**
  - Note test suite structure (unit, integration, e2e)
  - Capture test coverage distribution if observable

- **User Flows**
  - Trace complete user workflows from UI templates to backend

If critical information is **completely missing** (e.g. endpoints without definitions, or unknown authentication method), pause and return concise questions before continuing.

---

## 2. Required Output Files

Return **exactly eight** fenced code blocks. Each block begins with:

```text
FILE: docs/<file-name>
````

| File                    | Purpose                                    |
| ----------------------- | ------------------------------------------ |
| `architecture.md`       | Application structure and technology stack |
| `business_logic.md`     | User-facing features, workflows, rules     |
| `domain_model.md`       | Entities, relationships, constraints       |
| `database_structure.md` | Tables, migrations, indexing, schema       |
| `api_spec.yaml`         | OpenAPI 3.1 spec derived from code         |
| `auth_security.md`      | Auth methods, roles, session handling      |
| `user_flow_diagrams.md` | Mermaid diagrams for user journeys         |
| `README.md`             | Doc hub, diagram index, quick start        |

---

## 3. File Templates

### `architecture.md`

* Application type: microservices / monolith / hybrid
* Module/service catalog with short descriptions
* Mermaid `flowchart`:

  * Microservices: services and communications
  * Monolith: modules and interaction flows
* Tech stack summary
* Directory structure with folder purposes

---

### `business_logic.md`

Document use cases in this structure:

1. **Title**
2. **Actors**
3. **Step-by-step flow**
4. **Business rules**
5. **Validation logic**
6. Optional: `stateDiagram-v2` for entity lifecycle

---

### `domain_model.md`

* Entity table: `Entity | Description | Key fields (name:type:constraints)`
* Relationships and cardinalities
* Mermaid `erDiagram` of entity relationships
* Note compliance or data-retention concerns

---

### `database_structure.md`

* DB type and version (Postgres, MySQL, etc.)
* Connection config summary (not secrets)
* Per-table breakdown:

  * Columns with types/constraints
  * Indexes, foreign keys, triggers
* Mermaid `erDiagram`
* Migration strategy, seed data, performance tips

---

### `api_spec.yaml`

* Full OpenAPI 3.1 structure from code:

  * Paths, methods, schemas, auth
  * `$ref` schema reuse
  * Example requests/responses
  * Error format and rate limits (if any)

---

### `auth_security.md`

* Auth mechanisms (JWT, session, form-based)
* Roles and access control logic
* Security features: CSRF, headers, hashing
* Session management and login/logout flow
* Secrets & config strategy (no actual secrets)

---

### `user_flow_diagrams.md`

* Mapping table: route ↔ template ↔ action
* Mermaid `flowchart TD` for each major flow:

  * User steps, system responses
  * Form submissions and validations
  * Template files and endpoints with hrefs
* Visual formatting: HTML entities, emojis, links

---

### `README.md`

* App purpose and key features
* Quick start guide
* Links to all docs
* Diagram index:

  * Architecture: `flowchart`
  * User flows: `flowchart TD`
  * Domain: `erDiagram`
* Configuration variables
* Changelog (version, date, summary)

---

## 4. Formatting Rules

* Use GitHub Markdown for `.md` files
* All code, YAML, or diagrams must be inside fenced blocks
* Do **not** include implementation code
* If insufficient code evidence is available:

  * Skip or flag the section clearly
  * Ask for clarifying info *only if needed to proceed*
* End the response **exactly after the last `FILE:` block**
* No chat commentary, apologies, or explanations outside files
* Be deterministic and consistent across runs

---

## 5. Flask-Specific Parsing Rules (If Applicable)

* Detect blueprints and route decorators
* Parse SQLAlchemy models and relationships
* Form classes, validation patterns, and their use
* Match templates with routes and logic
* Include info from `migrations/`, `forms/`, and `services/`

---

## 6. Failure Modes

* If zero output files can be generated:

  * Return reason: e.g., "Codebase is empty"
* If partial output is possible:

  * Return generated files only
  * Note which are missing and why

```

---

Let me know if you want:
- A **lighter version** (for faster execution)
- **Multi-agent variant** (one file per agent)
- **Test prompt** for validating hallucination rate

Would you like to benchmark this version in Cursor or Copilot?
```
