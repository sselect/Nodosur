"""Genera el catálogo de servicios en Excel a partir de app/content.py."""

from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from app.content import AREAS, COMPANY, all_services

FONT = "Arial"
TEAL = "0F766E"
INK = "0F172A"
MUTED = "64748B"
INPUT_BLUE = "0000FF"
YELLOW = "FFF59D"
THIN = Side(style="thin", color="E2E8F0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CLP = '"$"#,##0;("$"#,##0);"-"'

CATALOG_PATH = Path(__file__).parent / "static" / "downloads" / "catalogo-servicios-nodosur.xlsx"


def _font(**kw) -> Font:
    return Font(name=FONT, **kw)


def _header_row(ws, row: int, headers: list[str]) -> None:
    for col, text in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=text)
        cell.font = _font(bold=True, color="FFFFFF", size=10)
        cell.fill = PatternFill("solid", fgColor=TEAL)
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = BORDER
    ws.row_dimensions[row].height = 30


def build_catalog(path: Path = CATALOG_PATH) -> Path:
    wb = Workbook()

    # ---------- Notas (supuestos) ----------
    notes = wb.active
    notes.title = "Notas"
    notes["A1"] = f"{COMPANY['name']} · Catálogo de servicios"
    notes["A1"].font = _font(bold=True, size=16, color=INK)
    notes["A2"] = COMPANY["tagline"]
    notes["A2"].font = _font(italic=True, color=MUTED)
    rows = [
        ("Fecha de emisión", date.today().strftime("%d-%m-%Y")),
        ("Moneda", "Pesos chilenos (CLP), valores netos"),
        ("Tasa IVA", 0.19),
        ("Validez", "Precios referenciales. La propuesta final se cierra tras el diagnóstico gratuito."),
        ("Contacto", COMPANY["email"]),
        ("Ubicación", COMPANY["location"]),
    ]
    for i, (label, value) in enumerate(rows, start=4):
        notes.cell(row=i, column=1, value=label).font = _font(bold=True)
        cell = notes.cell(row=i, column=2, value=value)
        cell.font = _font(color=INPUT_BLUE if label == "Tasa IVA" else INK)
    notes["B6"].number_format = "0%"
    notes["B6"].fill = PatternFill("solid", fgColor=YELLOW)
    notes["B6"].comment = Comment(
        "Tasa general de IVA en Chile (Ley sobre Impuesto a las Ventas y Servicios, DL 825). "
        "Fuente: SII, sii.cl. Todas las fórmulas de IVA usan esta celda.",
        "NodoSur",
    )
    notes["A12"] = "Cómo usar este archivo"
    notes["A12"].font = _font(bold=True, size=12)
    for i, line in enumerate(
        [
            "1. Hoja 'Catálogo': todos los servicios con precio neto, IVA y total. Usa los filtros del encabezado.",
            "2. Hoja 'Cotizador': escribe la cantidad (celdas amarillas) junto a cada código y obtén tu total estimado.",
            "3. Hoja 'Resumen por área': cuántos servicios hay y el precio de entrada de cada área.",
            "Los valores en azul son datos de entrada; los negros son fórmulas.",
        ],
        start=13,
    ):
        notes.cell(row=i, column=1, value=line).font = _font(color=INK)
    notes.column_dimensions["A"].width = 22
    notes.column_dimensions["B"].width = 90

    # ---------- Catálogo ----------
    ws = wb.create_sheet("Catálogo")
    ws["A1"] = f"Catálogo de servicios {COMPANY['name']}"
    ws["A1"].font = _font(bold=True, size=14, color=INK)
    ws["A2"] = "Precios netos en CLP. IVA calculado con la tasa de la hoja Notas (celda B6)."
    ws["A2"].font = _font(italic=True, color=MUTED, size=9)
    headers = [
        "Código",
        "Área",
        "Servicio",
        "Descripción",
        "Entregables",
        "Modalidad",
        "SLA",
        "Precio desde (CLP neto)",
        "IVA (CLP)",
        "Total con IVA (CLP)",
        "Unidad",
    ]
    _header_row(ws, 4, headers)
    services = all_services()
    first = 5
    for offset, svc in enumerate(services):
        r = first + offset
        values = [
            svc["code"],
            svc["area"],
            svc["name"],
            svc["description"],
            svc["deliverables"],
            svc["modality"],
            svc["sla"],
            svc["price_from"],
            f"=H{r}*Notas!$B$6",
            f"=H{r}+I{r}",
            svc["unit"],
        ]
        for col, value in enumerate(values, start=1):
            cell = ws.cell(row=r, column=col, value=value)
            cell.font = _font(size=9, color=INPUT_BLUE if col == 8 else INK, bold=col == 1)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER
            if col in (8, 9, 10):
                cell.number_format = CLP
        if offset % 2:
            for col in range(1, len(headers) + 1):
                ws.cell(row=r, column=col).fill = PatternFill("solid", fgColor="F8FAFC")
    last = first + len(services) - 1
    for col, width in enumerate([9, 18, 30, 48, 44, 16, 26, 14, 12, 14, 26], start=1):
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.freeze_panes = "D5"
    ws.auto_filter.ref = f"A4:K{last}"

    # ---------- Cotizador ----------
    qt = wb.create_sheet("Cotizador")
    qt["A1"] = "Cotizador rápido"
    qt["A1"].font = _font(bold=True, size=14, color=INK)
    qt["A2"] = (
        "Escribe la cantidad en las celdas amarillas (columna D). Ejemplo: SOP-01 con cantidad 1 = un mes de "
        "soporte N2. Los precios se leen del Catálogo."
    )
    qt["A2"].font = _font(italic=True, color=MUTED, size=9)
    _header_row(qt, 4, ["Código", "Servicio", "Precio unitario (CLP neto)", "Cantidad", "Subtotal (CLP neto)"])
    for offset, svc in enumerate(services):
        r = 5 + offset
        cat_r = first + offset
        qt.cell(row=r, column=1, value=f"='Catálogo'!A{cat_r}")
        qt.cell(row=r, column=2, value=f"='Catálogo'!C{cat_r}")
        qt.cell(
            row=r,
            column=3,
            value=f"=INDEX('Catálogo'!$H${first}:$H${last},MATCH(A{r},'Catálogo'!$A${first}:$A${last},0))",
        )
        example = 1 if svc["code"] == "SOP-01" else 0
        qty = qt.cell(row=r, column=4, value=example)
        qty.fill = PatternFill("solid", fgColor=YELLOW)
        qty.font = _font(color=INPUT_BLUE, size=9)
        qt.cell(row=r, column=5, value=f"=C{r}*D{r}")
        for col in range(1, 6):
            cell = qt.cell(row=r, column=col)
            cell.border = BORDER
            if col != 4:
                cell.font = _font(size=9, color="008000" if col in (1, 2, 3) else INK)
            if col in (3, 5):
                cell.number_format = CLP
    q_last = 5 + len(services) - 1
    dv = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True)
    dv.error = "La cantidad debe ser un número mayor o igual a 0"
    qt.add_data_validation(dv)
    dv.add(f"D5:D{q_last}")
    totals = [
        ("Subtotal neto", f"=SUM(E5:E{q_last})"),
        ("IVA", f"=E{q_last + 2}*Notas!$B$6"),
        ("Total con IVA", f"=E{q_last + 2}+E{q_last + 3}"),
    ]
    for i, (label, formula) in enumerate(totals):
        r = q_last + 2 + i
        qt.cell(row=r, column=4, value=label).font = _font(bold=True)
        cell = qt.cell(row=r, column=5, value=formula)
        cell.font = _font(bold=True, color=INK)
        cell.number_format = CLP
    for col, width in enumerate([10, 42, 22, 12, 20], start=1):
        qt.column_dimensions[get_column_letter(col)].width = width
    qt.freeze_panes = "A5"

    # ---------- Resumen por área ----------
    sm = wb.create_sheet("Resumen por área")
    sm["A1"] = "Resumen por área"
    sm["A1"].font = _font(bold=True, size=14, color=INK)
    _header_row(sm, 3, ["Área", "Descripción", "N° de servicios", "Precio de entrada (CLP neto)"])
    for i, area in enumerate(AREAS):
        r = 4 + i
        sm.cell(row=r, column=1, value=area["name"]).font = _font(bold=True, size=10)
        sm.cell(row=r, column=2, value=area["summary"]).font = _font(size=9)
        sm.cell(row=r, column=3, value=f"=COUNTIF('Catálogo'!$B${first}:$B${last},A{r})")
        price = sm.cell(
            row=r,
            column=4,
            value=f"=_xlfn.MINIFS('Catálogo'!$H${first}:$H${last},'Catálogo'!$B${first}:$B${last},A{r})",
        )
        price.number_format = CLP
        for col in range(1, 5):
            sm.cell(row=r, column=col).border = BORDER
            sm.cell(row=r, column=col).alignment = Alignment(vertical="top", wrap_text=True)
    total_r = 4 + len(AREAS)
    sm.cell(row=total_r, column=1, value="Total").font = _font(bold=True)
    sm.cell(row=total_r, column=3, value=f"=SUM(C4:C{total_r - 1})").font = _font(bold=True)
    for col, width in enumerate([24, 70, 16, 26], start=1):
        sm.column_dimensions[get_column_letter(col)].width = width

    wb.active = wb.sheetnames.index("Catálogo")
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path


if __name__ == "__main__":
    print(build_catalog())
