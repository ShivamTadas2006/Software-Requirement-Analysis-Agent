"""
Software Requirement Analysis Agent
GUI Application built with Python and Gradio.
"""
import os
import sys
import io
import time

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Ensure project root directory is in sys.path for cloud deployment (e.g. Render)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr
from dotenv import load_dotenv

from src.analyzer import RequirementAnalyzer
from src.validators import (
    compute_dashboard_metrics,
    format_overview_markdown,
    format_fr_dataframe,
    format_nfr_dataframe,
    format_actors_dataframe,
    format_use_cases_dataframe,
    format_ambiguities_dataframe,
    format_improved_reqs_dataframe,
    format_traceability_dataframe,
    format_quality_markdown,
)
from src.srs_generator import SRSGenerator
from src.exporters import export_to_markdown, export_to_txt, export_to_pdf

load_dotenv()

# Initialize analyzer
analyzer = RequirementAnalyzer()

# Pre-defined sample inputs
SAMPLES = {
    "🍕 Online Food Delivery System": (
        "Create an online food delivery system where customers can register, login, browse restaurants, "
        "add food to cart, place orders and track deliveries. Admin should manage restaurants, menus and users. "
        "The system should be fast, secure, and handle high traffic during peak meal hours. Restaurant managers "
        "must be able to update item availability, and delivery partners should receive turn-by-turn navigation."
    ),
    "🏥 Hospital Management System": (
        "Develop a hospital management system for patient registration, appointment scheduling with doctors, "
        "medical records management, laboratory test results, and billing. Doctors can view patient history and "
        "prescribe medications. Nurses record vitals. The system must maintain strict patient confidentiality, "
        "support emergency access, generate itemized invoices, and allow lab technicians to publish diagnostic reports quickly."
    ),
    "🎓 Smart Campus Portal": (
        "Build a smart campus portal where students can view course schedules, track attendance, check grades, "
        "and borrow library books. Faculty can post assignments and mark attendance. Librarian manages book inventory, "
        "issues, and overdue fines. The system should be accessible on mobile phones, integrate with campus single sign-on, "
        "send low-attendance alerts if below 75%, and sustain peak traffic during semester grade release."
    )
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_sample(sample_key: str) -> str:
    """Loads a pre-defined sample requirement into the textbox."""
    return SAMPLES.get(sample_key, "")


def render_dashboard_cards(metrics: dict) -> str:
    """Renders clean HTML/Markdown metric cards for the dashboard."""
    return f"""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin: 10px 0 20px 0;">
  <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 14px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="font-size: 26px; font-weight: 700;">{metrics.get('total_requirements', 0)}</div>
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">Total Requirements</div>
  </div>
  <div style="background: linear-gradient(135deg, #065f46, #10b981); color: white; padding: 14px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="font-size: 26px; font-weight: 700;">{metrics.get('functional_count', 0)}</div>
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">Functional (FR)</div>
  </div>
  <div style="background: linear-gradient(135deg, #581c87, #8b5cf6); color: white; padding: 14px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="font-size: 26px; font-weight: 700;">{metrics.get('non_functional_count', 0)}</div>
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">Non-Functional (NFR)</div>
  </div>
  <div style="background: linear-gradient(135deg, #991b1b, #ef4444); color: white; padding: 14px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="font-size: 26px; font-weight: 700;">{metrics.get('high_priority_count', 0)}</div>
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">High Priority</div>
  </div>
  <div style="background: linear-gradient(135deg, #9a3412, #f97316); color: white; padding: 14px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="font-size: 26px; font-weight: 700;">{metrics.get('ambiguous_count', 0)}</div>
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">Ambiguities</div>
  </div>
  <div style="background: linear-gradient(135deg, #854d0e, #eab308); color: white; padding: 14px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="font-size: 26px; font-weight: 700;">{metrics.get('missing_count', 0)}</div>
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">Missing Reqs</div>
  </div>
  <div style="background: linear-gradient(135deg, #0f766e, #14b8a6); color: white; padding: 14px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="font-size: 26px; font-weight: 700;">{metrics.get('actors_count', 0)}</div>
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">System Actors</div>
  </div>
  <div style="background: linear-gradient(135deg, #374151, #6b7280); color: white; padding: 14px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="font-size: 26px; font-weight: 700;">{metrics.get('use_cases_count', 0)}</div>
    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9;">Use Cases</div>
  </div>
</div>
"""


def on_analyze(raw_text, api_key, base_url, model, demo_mode):
    """Event handler for 'Analyze Requirements' button."""
    success, data, msg = analyzer.analyze(
        raw_requirements=raw_text,
        api_key=api_key,
        base_url=base_url,
        model_name=model,
        demo_mode=demo_mode
    )

    if not success:
        return (
            msg,  # status_box
            render_dashboard_cards({}),  # dashboard_cards
            "### ❌ Analysis could not be completed. Please check the error message above.",  # overview_md
            None,  # fr_df
            None,  # nfr_df
            None,  # actors_df
            None,  # use_cases_df
            "### ❌ Quality analysis pending.",  # quality_md
            None,  # ambiguities_df
            None,  # improved_df
            None,  # traceability_df
            "Click 'Generate SRS' after analyzing requirements.",  # srs_md
            {},  # state_data
            raw_text  # state_raw
        )

    # Compute metrics & dataframes
    metrics = compute_dashboard_metrics(data)
    dashboard_html = render_dashboard_cards(metrics)
    overview_md = format_overview_markdown(data)
    fr_df = format_fr_dataframe(data)
    nfr_df = format_nfr_dataframe(data)
    actors_df = format_actors_dataframe(data)
    use_cases_df = format_use_cases_dataframe(data)
    quality_md = format_quality_markdown(data)
    ambiguities_df = format_ambiguities_dataframe(data)
    improved_df = format_improved_reqs_dataframe(data)
    traceability_df = format_traceability_dataframe(data)

    status_display = f"### {msg}"

    return (
        status_display,
        dashboard_html,
        overview_md,
        fr_df,
        nfr_df,
        actors_df,
        use_cases_df,
        quality_md,
        ambiguities_df,
        improved_df,
        traceability_df,
        "✨ Analysis complete! Switch to the **'📄 SRS Document'** tab and click **'Generate SRS'** to compile the full specification.",
        data,
        raw_text
    )


def on_generate_srs(state_data, state_raw):
    """Event handler for 'Generate SRS' button."""
    if not state_data or not isinstance(state_data, dict):
        return (
            "⚠️ Please analyze requirements first before generating the SRS.",
            None,
            None,
            None
        )

    srs_text = SRSGenerator.generate_srs(state_data, state_raw or "")
    
    # Pre-generate downloadable files in outputs/
    sys_slug = state_data.get("system_overview", {}).get("system_name", "system").lower().replace(" ", "_")
    sys_slug = "".join(c for c in sys_slug if c.isalnum() or c == "_")[:30]
    
    ts = int(time.time())
    md_path = os.path.join(OUTPUT_DIR, f"SRS_{sys_slug}_{ts}.md")
    txt_path = os.path.join(OUTPUT_DIR, f"SRS_{sys_slug}_{ts}.txt")
    pdf_path = os.path.join(OUTPUT_DIR, f"SRS_{sys_slug}_{ts}.pdf")

    export_to_markdown(srs_text, md_path)
    export_to_txt(srs_text, txt_path)
    export_to_pdf(srs_text, state_data, pdf_path)

    return (
        srs_text,
        md_path,
        txt_path,
        pdf_path
    )


def clear_all():
    """Resets the UI."""
    return (
        "",  # input_text
        "### 👋 Welcome to Software Requirement Analysis Agent. Enter requirements or choose a sample to begin.",  # status
        render_dashboard_cards({}),  # dashboard
        "### 💡 Overview will appear here after analysis.",  # overview
        None, None, None, None,  # dfs
        "### 💡 Quality analysis will appear here after analysis.",  # quality
        None, None, None,  # dfs
        "Click 'Generate SRS' after analyzing requirements.",  # srs
        {},  # state_data
        "",  # state_raw
        None, None, None  # files
    )


# Custom CSS for modern styling
CUSTOM_CSS = """
.container { max-width: 1250px; margin: auto; }
.header-box {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 20px;
    border-left: 6px solid #3b82f6;
}
.header-title { font-size: 28px; font-weight: 800; letter-spacing: -0.5px; margin: 0; color: #f8fafc; }
.header-sub { font-size: 14px; color: #94a3b8; margin-top: 6px; }
.status-card { padding: 10px 16px; border-radius: 8px; margin-bottom: 12px; }
"""

with gr.Blocks(title="Software Requirement Analysis Agent") as demo:
    # State containers
    state_data = gr.State({})
    state_raw = gr.State("")

    # Header
    gr.HTML("""
    <div class="header-box" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid #3b82f6;">
        <div style="font-size: 28px; font-weight: 800; letter-spacing: -0.5px; color: #f8fafc;">
            SOFTWARE REQUIREMENT ANALYSIS AGENT
        </div>
        <div style="font-size: 15px; color: #94a3b8; margin-top: 6px;">
            AI-powered Requirement Engineering Assistant & SRS Generator (IEEE 830 / ISO 29148)
        </div>
    </div>
    """)

    # Top Section: Input & Controls
    with gr.Row():
        with gr.Column(scale=4):
            input_text = gr.Textbox(
                label="Project / Requirement Input",
                placeholder="Enter raw, unstructured software requirements here...\nExample: 'Create an online food delivery system where customers can register, login, browse restaurants, add food to cart, place orders and track deliveries. Admin should manage restaurants, menus and users.'",
                lines=5,
                max_lines=12
            )

            # Sample Quick Loaders
            with gr.Row():
                gr.Markdown("**Quick Load Examples:**")
                btn_food = gr.Button("🍕 Food Delivery", size="sm")
                btn_hospital = gr.Button("🏥 Hospital System", size="sm")
                btn_campus = gr.Button("🎓 Smart Campus", size="sm")

            with gr.Row():
                btn_analyze = gr.Button("🚀 Analyze Requirements", variant="primary", scale=2)
                btn_clear = gr.Button("🗑️ Clear", variant="secondary", scale=1)

        with gr.Column(scale=2):
            with gr.Accordion("⚙️ LLM & Viva Settings", open=False):
                default_key = os.getenv("GROQ_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
                default_base_url = os.getenv("GROQ_BASE_URL", "") or os.getenv("OPENAI_BASE_URL", "")
                if not default_base_url and os.getenv("GROQ_API_KEY"):
                    default_base_url = "https://api.groq.com/openai/v1"
                default_model = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile" if os.getenv("GROQ_API_KEY") else "gpt-4o-mini")

                api_key_input = gr.Textbox(
                    label="API Key (Groq / OpenAI - Optional if in .env)",
                    placeholder="gsk_... or sk-...",
                    type="password",
                    value=default_key
                )
                base_url_input = gr.Textbox(
                    label="Custom Base URL (Default: https://api.groq.com/openai/v1 for Groq)",
                    placeholder="https://api.groq.com/openai/v1",
                    value=default_base_url
                )
                model_input = gr.Textbox(
                    label="Model Name (e.g. llama-3.3-70b-versatile, llama-3.1-8b-instant, gpt-4o-mini)",
                    value=default_model
                )
                demo_mode_chk = gr.Checkbox(
                    label="⚡ Viva Demo Mode (Offline / Zero-API Key)",
                    value=True if not default_key else False,
                    info="Recommended for college viva: uses realistic pre-computed requirements analysis without consuming API credits."
                )

    # Status / Notification Area
    status_box = gr.Markdown("### 👋 Enter software requirements above and click **'Analyze Requirements'** to begin.")

    # Dashboard Metrics
    dashboard_cards = gr.HTML(render_dashboard_cards({}))

    gr.Markdown("---")
    gr.Markdown("## 📑 Analysis Results")

    # Tabbed Interface
    with gr.Tabs():
        with gr.Tab("📊 Overview"):
            overview_md = gr.Markdown("### 💡 System summary, features, assumptions, and risks will appear here.")

        with gr.Tab("⚙️ Functional Requirements"):
            gr.Markdown("#### Extracted Functional Requirements (FR-XXX)")
            fr_df = gr.Dataframe(
                headers=["Requirement ID", "Category", "Description", "Priority", "Rationale"],
                datatype=["str", "str", "str", "str", "str"],
                wrap=True,
                interactive=False
            )

        with gr.Tab("🛡️ Non-Functional Requirements"):
            gr.Markdown("#### Quality & Operational Constraints (NFR-XXX)")
            nfr_df = gr.Dataframe(
                headers=["Requirement ID", "Category", "Description", "Priority", "Measurable Metric"],
                datatype=["str", "str", "str", "str", "str"],
                wrap=True,
                interactive=False
            )

        with gr.Tab("👥 Actors & Use Cases"):
            gr.Markdown("#### Identified User Classes & Actors")
            actors_df = gr.Dataframe(
                headers=["Actor Name", "Role", "Responsibilities"],
                datatype=["str", "str", "str"],
                wrap=True,
                interactive=False
            )
            gr.Markdown("#### System Use Cases")
            use_cases_df = gr.Dataframe(
                headers=["Use Case ID", "Title", "Primary Actor", "Description", "Preconditions", "Main Flow", "Postconditions"],
                datatype=["str", "str", "str", "str", "str", "str", "str"],
                wrap=True,
                interactive=False
            )

        with gr.Tab("🔍 Quality Analysis"):
            quality_md = gr.Markdown("### 💡 Quality evaluation against IEEE 830 dimensions will appear here.")

        with gr.Tab("⚠️ Ambiguities"):
            gr.Markdown("#### Ambiguity Detection & Suggested Quantifiable Improvements")
            ambiguities_df = gr.Dataframe(
                headers=["Original Statement", "Problem Identified", "Suggested Measurable Improvement"],
                datatype=["str", "str", "str"],
                wrap=True,
                interactive=False
            )

        with gr.Tab("✨ Improved Requirements"):
            gr.Markdown("#### Defect-to-Improvement Mapping")
            improved_df = gr.Dataframe(
                headers=["Original Requirement", "Problem Identified", "Improved Requirement"],
                datatype=["str", "str", "str"],
                wrap=True,
                interactive=False
            )

        with gr.Tab("📋 Traceability Matrix"):
            gr.Markdown("#### Requirement Traceability Matrix (RTM)")
            traceability_df = gr.Dataframe(
                headers=["Requirement ID", "Requirement", "Source Statement", "Type", "Priority", "Related Use Case"],
                datatype=["str", "str", "str", "str", "str", "str"],
                wrap=True,
                interactive=False
            )

        with gr.Tab("📄 SRS Document"):
            gr.Markdown("#### Complete 20-Section Software Requirements Specification (IEEE 830 Standard)")
            with gr.Row():
                btn_gen_srs = gr.Button("📝 Generate SRS Document", variant="primary", scale=2)

            srs_md = gr.Markdown("Click **'Generate SRS Document'** above to compile the complete specification.")

            gr.Markdown("#### 📥 Export & Download SRS")
            with gr.Row():
                file_md = gr.File(label="Download Markdown (.md)", interactive=False)
                file_txt = gr.File(label="Download Plain Text (.txt)", interactive=False)
                file_pdf = gr.File(label="Download Formatted PDF (.pdf)", interactive=False)

    # Wire event handlers
    btn_food.click(fn=lambda: load_sample("🍕 Online Food Delivery System"), outputs=[input_text])
    btn_hospital.click(fn=lambda: load_sample("🏥 Hospital Management System"), outputs=[input_text])
    btn_campus.click(fn=lambda: load_sample("🎓 Smart Campus Portal"), outputs=[input_text])

    btn_analyze.click(
        fn=on_analyze,
        inputs=[input_text, api_key_input, base_url_input, model_input, demo_mode_chk],
        outputs=[
            status_box,
            dashboard_cards,
            overview_md,
            fr_df,
            nfr_df,
            actors_df,
            use_cases_df,
            quality_md,
            ambiguities_df,
            improved_df,
            traceability_df,
            srs_md,
            state_data,
            state_raw
        ]
    )

    btn_gen_srs.click(
        fn=on_generate_srs,
        inputs=[state_data, state_raw],
        outputs=[srs_md, file_md, file_txt, file_pdf]
    )

    btn_clear.click(
        fn=clear_all,
        inputs=[],
        outputs=[
            input_text,
            status_box,
            dashboard_cards,
            overview_md,
            fr_df,
            nfr_df,
            actors_df,
            use_cases_df,
            quality_md,
            ambiguities_df,
            improved_df,
            traceability_df,
            srs_md,
            state_data,
            state_raw,
            file_md,
            file_txt,
            file_pdf
        ]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print("=" * 60)
    print("[INFO] Launching Software Requirement Analysis Agent...")
    print(f"[INFO] Server Port: {port}")
    print("=" * 60)
    demo.launch(server_name="0.0.0.0", server_port=port, share=False)

