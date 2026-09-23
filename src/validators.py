"""
Validation and data transformation utilities for requirements analysis.
"""
from typing import Dict, Any, List
import pandas as pd


def validate_analysis_data(data: Any) -> Dict[str, Any]:
    """
    Validates that analysis data contains expected sections and formats.
    Provides safe defaults if any keys are missing or malformed.
    """
    if not isinstance(data, dict):
        data = {}

    defaults = {
        "system_overview": {
            "system_name": "Software System",
            "summary": "No overview provided.",
            "scope": "General system boundary."
        },
        "system_features": [],
        "functional_requirements": [],
        "non_functional_requirements": [],
        "actors": [],
        "use_cases": [],
        "business_rules": [],
        "constraints": [],
        "assumptions": [],
        "dependencies": [],
        "data_requirements": [],
        "external_interfaces": {
            "user_interfaces": "Standard web/mobile UI",
            "hardware_interfaces": "Standard computing devices",
            "software_interfaces": "Database & REST APIs",
            "communication_interfaces": "HTTPS / TCP/IP"
        },
        "security_requirements": [],
        "performance_requirements": [],
        "potential_risks": [],
        "ambiguities": [],
        "missing_requirements": [],
        "conflicting_requirements": [],
        "quality_analysis": {
            "correctness": {"status": "Needs Review", "findings": "Not assessed."},
            "completeness": {"status": "Needs Review", "findings": "Not assessed."},
            "consistency": {"status": "Needs Review", "findings": "Not assessed."},
            "unambiguity": {"status": "Needs Review", "findings": "Not assessed."},
            "verifiability": {"status": "Needs Review", "findings": "Not assessed."},
            "feasibility": {"status": "Needs Review", "findings": "Not assessed."},
            "traceability": {"status": "Needs Review", "findings": "Not assessed."}
        },
        "improved_requirements": [],
        "traceability_matrix": []
    }

    sanitized = {}
    for key, default_val in defaults.items():
        val = data.get(key)
        if val is None:
            sanitized[key] = default_val
        elif isinstance(default_val, dict) and isinstance(val, dict):
            # Nested merge
            merged = default_val.copy()
            merged.update(val)
            sanitized[key] = merged
        elif isinstance(default_val, list) and not isinstance(val, list):
            sanitized[key] = [val] if val else []
        else:
            sanitized[key] = val

    return sanitized


def compute_dashboard_metrics(data: Dict[str, Any]) -> Dict[str, int]:
    """
    Computes key summary statistics for the requirements dashboard.
    """
    fr_list = data.get("functional_requirements", [])
    nfr_list = data.get("non_functional_requirements", [])
    ambiguities = data.get("ambiguities", [])
    missing = data.get("missing_requirements", [])
    actors = data.get("actors", [])
    use_cases = data.get("use_cases", [])

    total_reqs = len(fr_list) + len(nfr_list)
    
    high_priority_count = 0
    for req in fr_list + nfr_list:
        if isinstance(req, dict) and str(req.get("priority", "")).strip().lower() == "high":
            high_priority_count += 1

    return {
        "total_requirements": total_reqs,
        "functional_count": len(fr_list),
        "non_functional_count": len(nfr_list),
        "ambiguous_count": len(ambiguities),
        "missing_count": len(missing),
        "high_priority_count": high_priority_count,
        "actors_count": len(actors),
        "use_cases_count": len(use_cases)
    }


def format_overview_markdown(data: Dict[str, Any]) -> str:
    """Formats system overview, features, constraints, assumptions, and risks into markdown."""
    overview = data.get("system_overview", {})
    features = data.get("system_features", [])
    constraints = data.get("constraints", [])
    assumptions = data.get("assumptions", [])
    dependencies = data.get("dependencies", [])
    risks = data.get("potential_risks", [])

    md = []
    md.append(f"### 🎯 System Name: **{overview.get('system_name', 'System')}**\n")
    md.append(f"**Summary:** {overview.get('summary', 'N/A')}\n")
    md.append(f"**Scope:** {overview.get('scope', 'N/A')}\n")

    md.append("\n#### 🚀 Key System Features")
    if features:
        for f in features:
            if isinstance(f, dict):
                md.append(f"- **{f.get('feature_id', 'SF')}: {f.get('name', 'Feature')}** — {f.get('description', '')}")
            else:
                md.append(f"- {f}")
    else:
        md.append("- No specific features identified.")

    md.append("\n#### 🔒 Assumptions & Constraints")
    md.append("**Assumptions:**")
    if assumptions:
        for a in assumptions:
            md.append(f"- {a}")
    else:
        md.append("- Standard operating environment assumed.")

    md.append("\n**Constraints:**")
    if constraints:
        for c in constraints:
            md.append(f"- {c}")
    else:
        md.append("- Standard platform constraints apply.")

    md.append("\n**Dependencies:**")
    if dependencies:
        for d in dependencies:
            md.append(f"- {d}")
    else:
        md.append("- No external dependencies noted.")

    md.append("\n#### ⚠️ Potential Risks & Mitigations")
    if risks:
        for r in risks:
            if isinstance(r, dict):
                md.append(f"- **{r.get('risk', 'Risk')}** (Likelihood: `{r.get('likelihood', 'Medium')}`, Impact: `{r.get('impact', 'Medium')}`) — *Mitigation:* {r.get('mitigation', 'N/A')}")
            else:
                md.append(f"- {r}")
    else:
        md.append("- None identified.")

    return "\n".join(md)


def format_fr_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Formats functional requirements into a pandas DataFrame."""
    items = data.get("functional_requirements", [])
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append({
                "Requirement ID": item.get("id", "FR-000"),
                "Category": item.get("category", "General"),
                "Description": item.get("description", ""),
                "Priority": item.get("priority", "Medium"),
                "Rationale": item.get("rationale", "")
            })
    if not rows:
        return pd.DataFrame(columns=["Requirement ID", "Category", "Description", "Priority", "Rationale"])
    return pd.DataFrame(rows)


def format_nfr_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Formats non-functional requirements into a pandas DataFrame."""
    items = data.get("non_functional_requirements", [])
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append({
                "Requirement ID": item.get("id", "NFR-000"),
                "Category": item.get("category", "General"),
                "Description": item.get("description", ""),
                "Priority": item.get("priority", "Medium"),
                "Measurable Metric": item.get("metric", "")
            })
    if not rows:
        return pd.DataFrame(columns=["Requirement ID", "Category", "Description", "Priority", "Measurable Metric"])
    return pd.DataFrame(rows)


def format_actors_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Formats actors into a pandas DataFrame."""
    actors = data.get("actors", [])
    rows = []
    for a in actors:
        if isinstance(a, dict):
            rows.append({
                "Actor Name": a.get("name", "User"),
                "Role": a.get("role", ""),
                "Responsibilities": a.get("responsibilities", "")
            })
    if not rows:
        return pd.DataFrame(columns=["Actor Name", "Role", "Responsibilities"])
    return pd.DataFrame(rows)


def format_use_cases_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Formats use cases into a pandas DataFrame."""
    use_cases = data.get("use_cases", [])
    rows = []
    for uc in use_cases:
        if isinstance(uc, dict):
            steps = uc.get("main_flow", [])
            steps_str = " -> ".join(steps) if isinstance(steps, list) else str(steps)
            rows.append({
                "Use Case ID": uc.get("id", "UC-000"),
                "Title": uc.get("title", ""),
                "Primary Actor": uc.get("primary_actor", ""),
                "Description": uc.get("description", ""),
                "Preconditions": uc.get("preconditions", "None"),
                "Main Flow": steps_str,
                "Postconditions": uc.get("postconditions", "None")
            })
    if not rows:
        return pd.DataFrame(columns=["Use Case ID", "Title", "Primary Actor", "Description", "Preconditions", "Main Flow", "Postconditions"])
    return pd.DataFrame(rows)


def format_ambiguities_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Formats ambiguities into a pandas DataFrame."""
    items = data.get("ambiguities", [])
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append({
                "Original Statement": item.get("original_statement", ""),
                "Problem Identified": item.get("problem", ""),
                "Suggested Measurable Improvement": item.get("suggested_improvement", "")
            })
    if not rows:
        return pd.DataFrame(columns=["Original Statement", "Problem Identified", "Suggested Measurable Improvement"])
    return pd.DataFrame(rows)


def format_improved_reqs_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Formats improved requirements into a pandas DataFrame."""
    items = data.get("improved_requirements", [])
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append({
                "Original Requirement": item.get("original", ""),
                "Problem Identified": item.get("problem", ""),
                "Improved Requirement": item.get("improved", "")
            })
    if not rows:
        return pd.DataFrame(columns=["Original Requirement", "Problem Identified", "Improved Requirement"])
    return pd.DataFrame(rows)


def format_traceability_dataframe(data: Dict[str, Any]) -> pd.DataFrame:
    """Formats traceability matrix into a pandas DataFrame."""
    items = data.get("traceability_matrix", [])
    rows = []
    for item in items:
        if isinstance(item, dict):
            rows.append({
                "Requirement ID": item.get("req_id", ""),
                "Requirement": item.get("requirement", ""),
                "Source Statement": item.get("source_statement", ""),
                "Type": item.get("type", "Functional"),
                "Priority": item.get("priority", "Medium"),
                "Related Use Case": item.get("related_use_case", "")
            })
    if not rows:
        return pd.DataFrame(columns=["Requirement ID", "Requirement", "Source Statement", "Type", "Priority", "Related Use Case"])
    return pd.DataFrame(rows)


def format_quality_markdown(data: Dict[str, Any]) -> str:
    """Formats the 7 IEEE quality characteristics into an evaluative report."""
    qa = data.get("quality_analysis", {})
    dimensions = [
        ("Correctness", "correctness", "Ensures specifications accurately reflect user needs without factual distortion."),
        ("Completeness", "completeness", "Verifies all required scenarios, edge cases, and interfaces are covered."),
        ("Consistency", "consistency", "Confirms no contradictory requirements or overlapping terminology exist."),
        ("Unambiguity", "unambiguity", "Ensures every requirement has exactly one interpretation and no vague terms."),
        ("Verifiability", "verifiability", "Verifies each requirement has measurable acceptance criteria for testing."),
        ("Feasibility", "feasibility", "Evaluates whether requirements can be implemented within standard technical bounds."),
        ("Traceability", "traceability", "Checks if requirements can be traced from business need to use cases and code.")
    ]

    status_badges = {
        "acceptable": "🟢 **Acceptable**",
        "needs improvement": "🟡 **Needs Improvement**",
        "critical issues": "🔴 **Critical Issues**"
    }

    md = ["### 📐 IEEE 830 / ISO 29148 Requirement Quality Analysis\n"]
    md.append("| Quality Characteristic | Standard Definition | Status Assessment | Findings & Observations |")
    md.append("|:-----------------------|:-------------------|:------------------|:------------------------|")

    for title, key, desc in dimensions:
        info = qa.get(key, {})
        status = info.get("status", "Needs Improvement") if isinstance(info, dict) else "Needs Improvement"
        findings = info.get("findings", "Assessment pending.") if isinstance(info, dict) else str(info)
        badge = status_badges.get(status.lower().strip(), f"⚪ **{status}**")
        md.append(f"| **{title}** | {desc} | {badge} | {findings} |")

    missing = data.get("missing_requirements", [])
    if missing:
        md.append("\n#### 🔍 Missing Requirements Identified:")
        for m in missing:
            if isinstance(m, dict):
                md.append(f"- **{m.get('area', 'Area')}:** {m.get('reason', '')} — *Recommendation:* {m.get('recommendation', '')}")
            else:
                md.append(f"- {m}")

    conflicts = data.get("conflicting_requirements", [])
    if conflicts:
        md.append("\n#### ⚡ Conflicting Requirements / Trade-offs:")
        for c in conflicts:
            if isinstance(c, dict):
                md.append(f"- **Conflict:** {c.get('conflict', '')} — *Resolution:* {c.get('resolution', '')}")
            else:
                md.append(f"- {c}")

    return "\n".join(md)
