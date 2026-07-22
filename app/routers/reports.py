import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.pdf_service import md_path_to_pdf_path

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("")
async def list_reports():
    """List all generated reports."""
    if not os.path.exists("reports"):
        return []
    files = os.listdir("reports")
    return [{"filename": f, "path": f"reports/{f}"} for f in sorted(files, reverse=True)]


@router.get("/{filename}")
async def download_report(filename: str):
    """Download a generated report by filename."""
    file_path = os.path.join("reports", filename)
    if not os.path.exists(file_path) or not os.path.abspath(file_path).startswith(
        os.path.abspath("reports")
    ):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        path=file_path,
        media_type="text/markdown",
        filename=filename,
    )

@router.get("/{filename}/pdf")
async def download_report_pdf(filename: str):
    """Download a generated report as a PDF."""
    if not filename.endswith(".md"):
        raise HTTPException(status_code=400, detail="Filename must end with .md")
        
    md_file_path = os.path.join("reports", filename)
    if not os.path.exists(md_file_path) or not os.path.abspath(md_file_path).startswith(
        os.path.abspath("reports")
    ):
        raise HTTPException(status_code=404, detail="Report not found")
        
    pdf_file_path = os.path.splitext(md_file_path)[0] + ".pdf"
    
    # Generate PDF if it doesn't already exist
    if not os.path.exists(pdf_file_path):
        try:
            await md_path_to_pdf_path(md_file_path)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {repr(e)}")
            
    pdf_filename = os.path.splitext(filename)[0] + ".pdf"
            
    return FileResponse(
        path=pdf_file_path,
        media_type="application/pdf",
        filename=pdf_filename,
    )
