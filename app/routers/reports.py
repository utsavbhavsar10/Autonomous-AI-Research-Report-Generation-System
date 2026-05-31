import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

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
