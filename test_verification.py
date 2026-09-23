"""
Verification script for Software Requirement Analysis Agent.
Tests core analysis, metrics computation, SRS compilation, and file exports.
"""
import sys
import os

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.analyzer import RequirementAnalyzer
from src.validators import compute_dashboard_metrics, validate_analysis_data
from src.srs_generator import SRSGenerator
from src.exporters import export_to_markdown, export_to_txt, export_to_pdf

def test_all():
    print("Testing imports... OK")
    analyzer = RequirementAnalyzer()

    sample_text = (
        "Create an online food delivery system where customers can register, login, browse restaurants, "
        "add food to cart, place orders and track deliveries. Admin should manage restaurants, menus and users."
    )

    print("Running analysis (Demo Mode)...")
    success, data, msg = analyzer.analyze(sample_text, demo_mode=True)
    print(f"Analysis Status: {success} | Message: {msg}")
    assert success, "Analysis failed"
    assert "functional_requirements" in data, "Missing functional_requirements"
    assert len(data["functional_requirements"]) > 0, "No functional requirements found"

    print(f"Extracted {len(data['functional_requirements'])} functional requirements.")
    print(f"Extracted {len(data['non_functional_requirements'])} non-functional requirements.")

    metrics = compute_dashboard_metrics(data)
    print("Dashboard Metrics Computed:", metrics)
    assert metrics["total_requirements"] == len(data["functional_requirements"]) + len(data["non_functional_requirements"])

    print("Compiling 20-Section IEEE 830 SRS...")
    srs = SRSGenerator.generate_srs(data, sample_text)
    print(f"SRS Document compiled successfully ({len(srs)} characters).")

    # Verify key sections
    for i in range(1, 21):
        assert f"{i}. " in srs, f"Missing section {i} in SRS"

    print("Testing file exports...")
    os.makedirs("outputs", exist_ok=True)
    md_path = export_to_markdown(srs, "outputs/test_srs.md")
    txt_path = export_to_txt(srs, "outputs/test_srs.txt")
    pdf_path = export_to_pdf(srs, data, "outputs/test_srs.pdf")

    assert os.path.exists(md_path), "Markdown export failed"
    assert os.path.exists(txt_path), "TXT export failed"
    assert os.path.exists(pdf_path), "PDF export failed"

    print(f"Markdown file size: {os.path.getsize(md_path)} bytes")
    print(f"TXT file size: {os.path.getsize(txt_path)} bytes")
    print(f"PDF file size: {os.path.getsize(pdf_path)} bytes")
    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all()
