from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.services.stats import get_thermal_summary, get_monthly_stats

# Configuración de Jinja2 Templates
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["Vistas Web & Fragmentos HTMX"])

@router.get("/", response_class=HTMLResponse, summary="Dashboard Principal")
def index_view(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    """Renderiza la vista principal del dashboard térmico."""
    summary = get_thermal_summary(session=session)
    months = get_monthly_stats(session=session)

    return templates.TemplateResponse(
        request=request,
        name="pages/index.html",
        context={
            "version": settings.VERSION,
            "summary": summary,
            "months": months,
            "sensor_path": settings.TEMP_SENSOR_PATH,
        },
    )

@router.get("/web/fragments/current-temp", response_class=HTMLResponse, summary="Fragmento HTMX: Temperatura Actual")
def fragment_current_temp(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    """Retorna el fragmento HTML actualizado de temperatura actual para sondeo de HTMX."""
    summary = get_thermal_summary(session=session)
    return templates.TemplateResponse(
        request=request,
        name="fragments/current_temp.html",
        context={
            "summary": summary,
        },
    )

@router.get("/web/fragments/stats-summary", response_class=HTMLResponse, summary="Fragmento HTMX: Resumen de Métricas")
def fragment_stats_summary(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    """Retorna el fragmento HTML con las tarjetas KPI de 24 horas."""
    summary = get_thermal_summary(session=session)
    return templates.TemplateResponse(
        request=request,
        name="fragments/stats_summary.html",
        context={
            "summary": summary,
        },
    )

@router.get("/web/fragments/monthly-table", response_class=HTMLResponse, summary="Fragmento HTMX: Tabla Mensual")
def fragment_monthly_table(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    """Retorna el fragmento HTML con el listado mensual previo."""
    months = get_monthly_stats(session=session)
    return templates.TemplateResponse(
        request=request,
        name="fragments/monthly_table.html",
        context={
            "months": months,
        },
    )

@router.get("/web/fragments/modal-history", response_class=HTMLResponse, summary="Fragmento HTMX: Modal Histórico")
def fragment_modal_history(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    """Retorna el fragmento HTML con el histórico completo para el modal."""
    months = get_monthly_stats(session=session)
    return templates.TemplateResponse(
        request=request,
        name="fragments/modal_history.html",
        context={
            "months": months,
        },
    )
