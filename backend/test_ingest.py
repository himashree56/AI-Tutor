import httpx
import asyncio
import os

BASE_URL = "http://127.0.0.1:8001"

async def ingest_pdf(file_path):
    print(f"\n--- INGESTING PDF: {file_path} ---")
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    url = f"{BASE_URL}/ingest/upload"
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f, "application/pdf")}
        async with httpx.AsyncClient(timeout=300.0) as client:
            try:
                res = await client.post(url, files=files)
                res.raise_for_status()
                print(f"Success: {res.json()}")
            except Exception as e:
                print(f"Ingestion failed: {e}")

if __name__ == "__main__":
    pdf_path = r"C:\new\AI-tutor\BEE654B-module-5-pdf.pdf"
    asyncio.run(ingest_pdf(pdf_path))
