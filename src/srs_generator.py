"""
SRS Generator module for compiling an IEEE 830 / ISO 29148 compliant Software Requirements Specification.
"""
from typing import Dict, Any
from datetime import datetime


class SRSGenerator:
    """
    Compiles structured requirement analysis data into a formal, 20-section SRS document.
    """

    @staticmethod
    def generate_srs(analysis_data: Dict[str, Any], raw_requirements: str) -> str:
        """
        Compiles a comprehensive 20-section SRS document in GitHub-flavored Markdown.
        """
        overview = analysis_data.get("system_overview", {})
        sys_name = overview.get("system_name", "Software System")
        summary = overview.get("summary", "Software Requirements Specification")
        scope = overview.get("scope", "System boundaries defined herein.")

        features = analysis_data.get("system_features", [])
        fr_list = analysis_data.get("functional_requirements", [])
        nfr_list = analysis_data.get("non_functional_requirements", [])
        actors = analysis_data.get("actors", [])
        use_cases = analysis_data.get("use_cases", [])
        business_rules = analysis_data.get("business_rules", [])
        constraints = analysis_data.get("constraints", [])
        assumptions = analysis_data.get("assumptions", [])
        dependencies = analysis_data.get("dependencies", [])
        data_reqs = analysis_data.get("data_requirements", [])
        ext_interfaces = analysis_data.get("external_interfaces", {})
        security_reqs = analysis_data.get("security_requirements", [])
        perf_reqs = analysis_data.get("performance_requirements", [])
        risks = analysis_data.get("potential_risks", [])
        ambiguities = analysis_data.get("ambiguities", [])
        missing_reqs = analysis_data.get("missing_requirements", [])
        conflicts = analysis_data.get("conflicting_requirements", [])
        traceability = analysis_data.get("traceability_matrix", [])

        now_str = datetime.now().strftime("%B %d, %Y")

        doc = []
        doc.append(f"# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)")
        doc.append(f"## Project Title: {sys_name}")
        doc.append(f"**Document Version:** 1.0.0  ")
        doc.append(f"**Standard:** IEEE Std 830-1998 / ISO/IEC/IEEE 29148:2018  ")
        doc.append(f"**Date Generated:** {now_str}  ")
        doc.append(f"**Prepared By:** Software Requirement Analysis Agent  ")
        doc.append("\n---\n")

        # Table of Contents
        doc.append("## Table of Contents")
        doc.append("1. [Introduction](#1-introduction)")
        doc.append("2. [Purpose](#2-purpose)")
        doc.append("3. [Scope](#3-scope)")
        doc.append("4. [Definitions, Acronyms, and Abbreviations](#4-definitions-acronyms-and-abbreviations)")
        doc.append("5. [Overall Description](#5-overall-description)")
        doc.append("6. [Product Perspective](#6-product-perspective)")
        doc.append("7. [User Classes and Characteristics](#7-user-classes-and-characteristics)")
        doc.append("8. [Functional Requirements](#8-functional-requirements)")
        doc.append("9. [Non-Functional Requirements](#9-non-functional-requirements)")
        doc.append("10. [External Interface Requirements](#10-external-interface-requirements)")
        doc.append("11. [Data Requirements & Schema Entities](#11-data-requirements--schema-entities)")
        doc.append("12. [Business Rules](#12-business-rules)")
        doc.append("13. [Assumptions and Dependencies](#13-assumptions-and-dependencies)")
        doc.append("14. [Constraints](#14-constraints)")
        doc.append("15. [Security Requirements](#15-security-requirements)")
        doc.append("16. [Performance Requirements](#16-performance-requirements)")
        doc.append("17. [Potential Risks and Mitigation Strategies](#17-potential-risks-and-mitigation-strategies)")
        doc.append("18. [Use Cases & System Workflows](#18-use-cases--system-workflows)")
        doc.append("19. [Ambiguous and Missing Requirements Analysis](#19-ambiguous-and-missing-requirements-analysis)")
        doc.append("20. [Traceability Matrix](#20-traceability-matrix)")
        doc.append("\n---\n")

        # 1. Introduction
        doc.append("### 1. Introduction")
        doc.append(f"This document provides the formal Software Requirements Specification (SRS) for **{sys_name}**. "
                   f"The requirements compiled herein establish the definitive functional and qualitative baselines "
                   f"agreed upon between domain stakeholders, developers, and quality assurance engineers.")
        doc.append(f"\n**Original User Specification:**\n> *\"{raw_requirements.strip()}\"*")

        # 2. Purpose
        doc.append("\n### 2. Purpose")
        doc.append(f"The primary purpose of this specification is to articulate the functional capabilities, performance criteria, "
                   f"and system constraints for {sys_name}. This document serves as the foundational artifact for system architecture "
                   f"design, implementation, test case formulation, and formal verification.")

        # 3. Scope
        doc.append("\n### 3. Scope")
        doc.append(f"**In-Scope Boundaries:** {scope}\n")
        doc.append(f"The system aims to fulfill the following core functions: {summary}\n")
        doc.append("**Out-of-Scope Items:** Features not explicitly enumerated in Section 8 or 10 are considered out of scope "
                   "for the initial product release milestone and subject to subsequent change request approval.")

        # 4. Definitions
        doc.append("\n### 4. Definitions, Acronyms, and Abbreviations")
        doc.append("| Term / Acronym | Definition |")
        doc.append("|:--------------|:-----------|")
        doc.append("| **SRS** | Software Requirements Specification (IEEE 830 compliant) |")
        doc.append("| **FR** | Functional Requirement |")
        doc.append("| **NFR** | Non-Functional Requirement |")
        doc.append("| **UC** | Use Case |")
        doc.append("| **BR** | Business Rule |")
        doc.append("| **RBAC** | Role-Based Access Control |")
        doc.append("| **API** | Application Programming Interface |")
        doc.append("| **TLS** | Transport Layer Security (Cryptographic communication protocol) |")

        # 5. Overall Description
        doc.append("\n### 5. Overall Description")
        doc.append(f"{summary}\n")
        doc.append("#### Major System Features:")
        if features:
            for f in features:
                doc.append(f"- **{f.get('feature_id', 'SF')}: {f.get('name', '')}** — {f.get('description', '')}")
        else:
            doc.append("- Modular services supporting user interactions, processing logic, and data persistence.")

        # 6. Product Perspective
        doc.append("\n### 6. Product Perspective")
        doc.append(f"{sys_name} is conceived as a self-contained, multi-tier software system communicating via standardized "
                   "web protocols. It interfaces with external client terminals (desktop/mobile browsers) and backend database "
                   "and notification engines.")
        doc.append("\n```\n+-------------------------------------------------------------+\n"
                   "|                     Presentation Tier                       |\n"
                   "|     (Web Browser UI / Mobile Application Client)             |\n"
                   "+------------------------------+------------------------------+\n"
                   "                               | HTTPS / WSS\n"
                   "                               v\n"
                   "+-------------------------------------------------------------+\n"
                   "|                      Application Tier                       |\n"
                   "|   (API Gateway, Business Logic, Auth & Routing Controllers) |\n"
                   "+------------------------------+------------------------------+\n"
                   "                               |\n"
                   "        +----------------------+----------------------+\n"
                   "        v                                             v\n"
                   "+-----------------------------+              +-----------------------------+\n"
                   "|         Data Tier           |              |      External Services      |\n"
                   "|  (Relational Database/Cache)|              |  (Payment / Notification)   |\n"
                   "+-----------------------------+              +-----------------------------+\n```")

        # 7. User Classes
        doc.append("\n### 7. User Classes and Characteristics")
        doc.append("| User Class / Actor | Role & Hierarchy | Key Responsibilities |")
        doc.append("|:-------------------|:-----------------|:---------------------|")
        if actors:
            for a in actors:
                doc.append(f"| **{a.get('name', 'Actor')}** | {a.get('role', '')} | {a.get('responsibilities', '')} |")
        else:
            doc.append("| End User | General User | Interacts with primary system workflows |")

        # 8. Functional Requirements
        doc.append("\n### 8. Functional Requirements")
        doc.append("| ID | Category | Requirement Statement | Priority | Rationale |")
        doc.append("|:---|:---------|:----------------------|:---------|:----------|")
        if fr_list:
            for fr in fr_list:
                doc.append(f"| **{fr.get('id', 'FR')}** | {fr.get('category', 'General')} | {fr.get('description', '')} | {fr.get('priority', 'Medium')} | {fr.get('rationale', '')} |")
        else:
            doc.append("| FR-001 | General | The system shall perform core operations. | Medium | Baseline operation |")

        # 9. Non-Functional Requirements
        doc.append("\n### 9. Non-Functional Requirements")
        doc.append("| ID | Category | Requirement Statement | Priority | Acceptance Metric |")
        doc.append("|:---|:---------|:----------------------|:---------|:------------------|")
        if nfr_list:
            for nfr in nfr_list:
                doc.append(f"| **{nfr.get('id', 'NFR')}** | {nfr.get('category', 'General')} | {nfr.get('description', '')} | {nfr.get('priority', 'Medium')} | {nfr.get('metric', '')} |")
        else:
            doc.append("| NFR-001 | Performance | The system shall respond within 2 seconds. | High | Latency <= 2000ms |")

        # 10. External Interface Requirements
        doc.append("\n### 10. External Interface Requirements")
        doc.append(f"- **User Interfaces:** {ext_interfaces.get('user_interfaces', 'Responsive graphical user interface.')}")
        doc.append(f"- **Hardware Interfaces:** {ext_interfaces.get('hardware_interfaces', 'Standard client hardware.')}")
        doc.append(f"- **Software Interfaces:** {ext_interfaces.get('software_interfaces', 'RDBMS and external REST web services.')}")
        doc.append(f"- **Communication Interfaces:** {ext_interfaces.get('communication_interfaces', 'Encrypted HTTPS / TLS 1.3 protocol.')}")

        # 11. Data Requirements
        doc.append("\n### 11. Data Requirements & Schema Entities")
        if data_reqs:
            doc.append("| Entity Name | Attributes | Description & Persistence |")
            doc.append("|:------------|:-----------|:--------------------------|")
            for d in data_reqs:
                doc.append(f"| **{d.get('entity', 'Entity')}** | `{d.get('attributes', '')}` | {d.get('description', '')} |")
        else:
            doc.append("- Standard relational schema entities required for user accounts and transaction records.")

        # 12. Business Rules
        doc.append("\n### 12. Business Rules")
        if business_rules:
            for br in business_rules:
                doc.append(f"- **{br.get('id', 'BR-001')}:** {br.get('rule', '')} *(Rationale: {br.get('rationale', '')})*")
        else:
            doc.append("- Standard system operational rules apply.")

        # 13. Assumptions and Dependencies
        doc.append("\n### 13. Assumptions and Dependencies")
        doc.append("#### Assumptions:")
        if assumptions:
            for a in assumptions:
                doc.append(f"- {a}")
        else:
            doc.append("- Continuous network availability is assumed for client-server communication.")

        doc.append("\n#### Dependencies:")
        if dependencies:
            for dep in dependencies:
                doc.append(f"- {dep}")
        else:
            doc.append("- Standard runtime execution environment.")

        # 14. Constraints
        doc.append("\n### 14. Constraints")
        if constraints:
            for c in constraints:
                doc.append(f"- {c}")
        else:
            doc.append("- Compliance with standard web accessibility and security protocols.")

        # 15. Security Requirements
        doc.append("\n### 15. Security Requirements")
        if security_reqs:
            for sec in security_reqs:
                doc.append(f"- **{sec.get('id', 'SEC')}:** {sec.get('description', '')} `[{sec.get('priority', 'High')}]`")
        else:
            doc.append("- Authentication and data encryption at rest and in transit.")

        # 16. Performance Requirements
        doc.append("\n### 16. Performance Requirements")
        if perf_reqs:
            for pr in perf_reqs:
                doc.append(f"- **{pr.get('id', 'PERF')}:** {pr.get('requirement', '')} *(Metric: `{pr.get('metric', '')}`)*")
        else:
            doc.append("- Response times must not exceed 2.0 seconds under normal load conditions.")

        # 17. Risks
        doc.append("\n### 17. Potential Risks and Mitigation Strategies")
        if risks:
            doc.append("| Risk Description | Likelihood | Impact | Recommended Mitigation |")
            doc.append("|:-----------------|:-----------|:-------|:-----------------------|")
            for r in risks:
                doc.append(f"| {r.get('risk', '')} | `{r.get('likelihood', 'Medium')}` | `{r.get('impact', 'Medium')}` | {r.get('mitigation', '')} |")
        else:
            doc.append("- General operational software deployment risks apply.")

        # 18. Use Cases
        doc.append("\n### 18. Use Cases & System Workflows")
        if use_cases:
            for uc in use_cases:
                doc.append(f"#### {uc.get('id', 'UC')}: {uc.get('title', 'Use Case')}")
                doc.append(f"- **Primary Actor:** {uc.get('primary_actor', 'User')}")
                doc.append(f"- **Description:** {uc.get('description', '')}")
                doc.append(f"- **Preconditions:** {uc.get('preconditions', 'None')}")
                doc.append(f"- **Postconditions:** {uc.get('postconditions', 'None')}")
                doc.append("- **Main Success Scenario:**")
                flow = uc.get("main_flow", [])
                if isinstance(flow, list):
                    for step in flow:
                        doc.append(f"  1. {step.replace('Step ', '') if step.startswith('Step ') else step}")
                else:
                    doc.append(f"  1. {flow}")
                doc.append("")
        else:
            doc.append("- Core use cases defined in functional requirements section.")

        # 19. Ambiguous and Missing Requirements
        doc.append("\n### 19. Ambiguous and Missing Requirements Analysis")
        doc.append("#### Ambiguity Resolution:")
        if ambiguities:
            doc.append("| Original Ambiguous Statement | Problem Identified | Formal Measurable Revision |")
            doc.append("|:-----------------------------|:-------------------|:---------------------------|")
            for amb in ambiguities:
                doc.append(f"| *\"{amb.get('original_statement', '')}\"* | {amb.get('problem', '')} | **{amb.get('suggested_improvement', '')}** |")
        else:
            doc.append("- No critical ambiguities detected in original text.")

        doc.append("\n#### Missing Requirements Recommendations:")
        if missing_reqs:
            for m in missing_reqs:
                doc.append(f"- **{m.get('area', 'Area')}:** {m.get('reason', '')} *(Recommended Action: {m.get('recommendation', '')})*")
        else:
            doc.append("- Requirement coverage is sufficient for baseline architecture.")

        if conflicts:
            doc.append("\n#### Conflicting Constraints:")
            for c in conflicts:
                doc.append(f"- **Conflict:** {c.get('conflict', '')} *(Resolution: {c.get('resolution', '')})*")

        # 20. Traceability Matrix
        doc.append("\n### 20. Traceability Matrix")
        doc.append("| Req ID | Requirement Description | Source Input Phrase | Type | Priority | Associated Use Case |")
        doc.append("|:-------|:------------------------|:-------------------|:-----|:---------|:---------------------|")
        if traceability:
            for tr in traceability:
                doc.append(f"| **{tr.get('req_id', '')}** | {tr.get('requirement', '')} | *\"{tr.get('source_statement', '')}\"* | {tr.get('type', 'Functional')} | {tr.get('priority', 'Medium')} | `{tr.get('related_use_case', 'UC-001')}` |")
        else:
            doc.append("| FR-001 | Core Functionality | Raw input statement | Functional | High | UC-001 |")

        doc.append("\n---\n*End of Software Requirements Specification Document.*")

        return "\n".join(doc)
