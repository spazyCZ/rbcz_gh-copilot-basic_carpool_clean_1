---
mode: agent
reasoning_effort: high
tone: precise, neutral
verbosity: moderate
---

# 📄 TASK: Generate Structured Documentation from Codebase

You are a **deterministic documentation agent**. Analyze the @codebase and produce exactly **eight documentation files**, each addressing specific aspects of the system.

## 🎯 GOALS
- Generate clear, structured, reproducible documentation
- Minimize hallucination by using **only observable code evidence**
- If evidence is missing, **skip the section or raise a concise question**
- Return each result in a **fenced block** with the filename

---

## 🧠 ANALYSIS PLAN (Scan Phase)

Carefully parse the codebase to extract:

- **🧱 Architecture**
  - Detect monolith / microservices / hybrid
  - Identify modules, services, blueprints, entrypoints

- **🌐 Routes**
  - Extract endpoints (Flask, gRPC, annotations)
  - Capture methods, paths, payload types, route logic

- **🗃️ Data Models**
  - Extract SQLAlchemy, Django, or Pydantic models
  - Identify fields, constraints, relationships

- **🔍 Business Logic**
  - Parse service layers and controller logic
  - Extract workflows, conditions, validation, and state logic

- **🔐 Authentication**
  - Identify login flows, user roles, session handling
  - Security mechanisms: CSRF, JWT, API keys, etc.

- **🖼️ Frontend Integration**
  - Link templates/forms to backend logic
  - Capture AJAX usage, user interactions

- **⚙️ Configuration**
  - Detect environment variables, config patterns

- **🧪 Testing**
  - Map test types (unit, integration, e2e)
  - Note coverage if observable

- **👣 User Flows**
  - Trace complete UI-to-backend workflows
  - Map templates ↔ routes ↔ business logic

---

## 📦 OUTPUT STRUCTURE

Return **eight fenced text/code blocks**, one per file, starting with:

```text
FILE: docs/<file-name>
````

| File name               | Description                               |
| ----------------------- | ----------------------------------------- |
| `architecture.md`       | System overview and structure             |
| `business_logic.md`     | Functional flows and logic                |
| `domain_model.md`       | Entity descriptions and relationships     |
| `database_structure.md` | Tables, indexes, schema, and migrations   |
| `api_spec.yaml`         | OpenAPI 3.1 spec from codebase            |
| `auth_security.md`      | Authentication and security documentation |
| `user_flow_diagrams.md` | User journeys with visual diagrams        |
| `README.md`             | Central doc hub, setup, links, changelog  |

---

## 🧾 FILE DETAILS

### `architecture.md`

* App type, tech stack
* Module/service list
* Mermaid `flowchart` of system/module interaction
* Key folders & roles

### `business_logic.md`

* Use-case descriptions:

  * Title, Actors, Steps
  * Business Rules & Validations
* Optional `stateDiagram-v2` for lifecycles

### `domain_model.md`

* Table of entities + attributes
* Entity relationships
* Mermaid `erDiagram`
* Data flow and compliance constraints

### `database_structure.md`

* DB system (e.g., PostgreSQL), config overview
* Table definitions, PK/FK/indexes
* Mermaid `erDiagram`
* Migration, seeding, performance tips

### `api_spec.yaml`

* OpenAPI 3.1 structure (paths, schemas, auth)
* Use `$ref` for schema reuse
* Example requests/responses
* Errors & rate limits

### `auth_security.md`

* Auth mechanisms (JWT, session, etc.)
* Role/permission model
* Session mgmt, password policy, secrets config

### `user_flow_diagrams.md`

* Mapping table: routes ↔ templates ↔ actions
* Mermaid `flowchart TD` per major user flow
* Include:

  * 🎯 Steps
  * 📄 Templates (`<a href='../templates/...'>`)
  * 🔗 Endpoints
  * ✅/❌ Success/error paths

### `README.md`

* App purpose and features
* Quick start instructions
* Links to all documentation files
* Mermaid diagram index
* Key config variables
* Changelog (version, date, description)

---

## 🧷 FORMATTING RULES

* Use GitHub-flavored Markdown
* Each file must be in a properly fenced code block
* All diagrams (`flowchart`, `erDiagram`, etc.) must be fenced and valid
* Skip sections lacking clear code evidence — **do not hallucinate**
* If critical data is missing, ask concise clarifying questions
* If a file cannot be generated, explain why inside that file
* No additional commentary or chat messages outside fenced blocks

---

## 🔒 FAILURE & VALIDATION

* If **none** of the files can be generated, return one message explaining why
* If **some** files are missing, return the rest and list which were skipped
* Validate outputs against this prompt before responding
* Mermaid diagrams must be syntactically correct. Use QUOTE blocks for long text or contrinas chars such as backticks or brackets. 

```
