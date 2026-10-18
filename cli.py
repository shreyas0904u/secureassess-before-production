import asyncio
import argparse
import sys
import os

# Add backend directory to Python path so absolute imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models.database import init_db, create_assessment, get_assessment, get_findings
from backend.engine.orchestrator import run_demo_assessment
from backend.reports.generator import generate_report

async def progress_callback(phase_id, phase_name, percent, message):
    """Callback to print progress to the terminal."""
    sys.stdout.write(f"\r[{percent}%] {phase_name}: {message}".ljust(80))
    sys.stdout.flush()
    if percent >= 100:
        print("\n")

async def main():
    parser = argparse.ArgumentParser(description="SecureAssess CLI Engine")
    parser.add_argument("--target", required=True, help="Live target URL (e.g., https://www.worldmonitor.app)")
    parser.add_argument("--source", required=True, help="Local source code path (e.g., C:\\path\\to\\code)")
    args = parser.parse_args()

    print(f"[*] Initializing SecureAssess Engine...")
    print(f"[*] Target URL: {args.target}")
    print(f"[*] Source Path: {args.source}")
    print("-" * 60)

    # 1. Initialize the SQLite database
    await init_db()

    # 2. Create a new assessment record (is_demo=True)
    assessment_record = await create_assessment(target_url=args.target, source_path=args.source, is_demo=True)
    assessment_id = assessment_record["id"]

    # 3. Run the fast demonstration engine
    try:
        results = await run_demo_assessment(assessment_id, args.target, progress_callback)
    except Exception as e:
        print(f"\n[!] Assessment failed: {e}")
        sys.exit(1)

    print("-" * 60)
    print(f"[+] Security Score: {results['security_score']}/100")
    print(f"[+] Total Findings: {results['total_findings']}")
    
    # 4. Generate the PDF
    print("[*] Generating PDF Report...")
    assessment = await get_assessment(assessment_id)
    findings = await get_findings(assessment_id)
    
    pdf_bytes = generate_report(assessment, findings)
    
    # 5. Save the PDF to the current directory
    filename = f"security-report-{assessment_id}.pdf"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)
        
    print(f"[+] Success! PDF Report saved to: {filepath}")

if __name__ == "__main__":
    # Ensure Windows asyncio works correctly
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
