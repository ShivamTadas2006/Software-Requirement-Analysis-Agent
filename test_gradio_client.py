"""
End-to-End Gradio Client test script for Software Requirement Analysis Agent.
"""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from gradio_client import Client

def main():
    print("Connecting to running Gradio app at http://127.0.0.1:7860...")
    client = Client("http://127.0.0.1:7860/")

    # 1. Test Quick Sample Loader
    print("\n--- 1. Testing Sample 1 (Food Delivery) Loader ---")
    sample_text = client.predict(api_name="/lambda")
    print(f"Loaded Sample Text (length: {len(sample_text)}): {sample_text[:80]}...")
    assert "food delivery system" in sample_text.lower()

    # 2. Test Analysis Endpoint
    print("\n--- 2. Testing /on_analyze Endpoint ---")
    result = client.predict(
        raw_text=sample_text,
        api_key="",
        base_url="",
        model="gpt-4o-mini",
        demo_mode=True,
        api_name="/on_analyze"
    )

    status_msg = result[0]
    dashboard_html = result[1]
    overview_md = result[2]
    fr_data = result[3]
    nfr_data = result[4]
    actors_data = result[5]
    use_cases_data = result[6]
    quality_md = result[7]
    ambiguities_data = result[8]
    improved_data = result[9]
    traceability_data = result[10]

    print("Status Message:", status_msg)
    print("Dashboard HTML length:", len(dashboard_html))
    print("Functional Requirements count:", len(fr_data["data"]))
    print("Non-Functional Requirements count:", len(nfr_data["data"]))
    print("Actors count:", len(actors_data["data"]))
    print("Use Cases count:", len(use_cases_data["data"]))
    print("Ambiguities count:", len(ambiguities_data["data"]))
    print("Improved Requirements count:", len(improved_data["data"]))
    print("Traceability Matrix rows:", len(traceability_data["data"]))

    assert len(fr_data["data"]) >= 5
    assert len(nfr_data["data"]) >= 3
    assert len(actors_data["data"]) >= 2
    assert len(use_cases_data["data"]) >= 2

    # 3. Test Generate SRS Endpoint
    print("\n--- 3. Testing /on_generate_srs Endpoint ---")
    srs_result = client.predict(api_name="/on_generate_srs")
    srs_text = srs_result[0]
    file_md = srs_result[1]
    file_txt = srs_result[2]
    file_pdf = srs_result[3]

    print(f"Generated SRS length: {len(srs_text)} chars")
    print(f"Downloaded Markdown path: {file_md}")
    print(f"Downloaded TXT path: {file_txt}")
    print(f"Downloaded PDF path: {file_pdf}")

    assert "SOFTWARE REQUIREMENTS SPECIFICATION" in srs_text
    assert "1. Introduction" in srs_text
    assert "20. Traceability Matrix" in srs_text
    assert file_md and file_txt and file_pdf

    # 4. Test Clear All
    print("\n--- 4. Testing /clear_all Endpoint ---")
    clear_result = client.predict(api_name="/clear_all")
    print("Cleared input text:", repr(clear_result[0]))
    assert clear_result[0] == ""

    print("\n==========================================")
    print("🎉 ALL GRADIO ENDPOINTS VERIFIED 100% WORKING!")
    print("==========================================")

if __name__ == "__main__":
    main()
