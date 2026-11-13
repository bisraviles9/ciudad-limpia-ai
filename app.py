import csv
import io
import json
from datetime import datetime
from pathlib import Path

import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
REPORTS_FILE = DATA_DIR / "reports.json"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Ciudad Limpia AI", page_icon="🌱", layout="wide")


def load_reports():
    if not REPORTS_FILE.exists():
        return []
    try:
        return json.loads(REPORTS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_reports(reports):
    REPORTS_FILE.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")


st.title("🌱 Ciudad Limpia AI")
st.caption("Reporta acumulaciones de basura, ubícalas en el mapa y ayuda a priorizar la limpieza.")

reports = load_reports()
report_tab, map_tab, municipal_tab = st.tabs(["📸 Nuevo reporte", "🗺️ Mapa de zonas", "🏛️ Panel municipal"])

with report_tab:
    st.subheader("Reportar un punto")
    st.info("MVP comunitario: la identificación inicial se basa en la categoría y confirmación de la persona que reporta. No se envían fotos a servicios externos ni se afirma usar un modelo automático de visión.")
    with st.form("new_report", clear_on_submit=True):
        photo = st.file_uploader("Fotografía del lugar", type=["jpg", "jpeg", "png", "webp"])
        left, right = st.columns(2)
        with left:
            category = st.selectbox("Tipo de residuo", ["Basura mezclada", "Plástico", "Escombros", "Residuos orgánicos", "Otro"])
            description = st.text_area("Descripción breve", placeholder="Ej.: bolsas junto al parque")
            neighborhood = st.text_input("Barrio o referencia")
        with right:
            latitude = st.number_input("Latitud", min_value=-90.0, max_value=90.0, value=-0.1807, format="%.6f", help="Puedes copiar las coordenadas del mapa de tu teléfono.")
            longitude = st.number_input("Longitud", min_value=-180.0, max_value=180.0, value=-78.4678, format="%.6f")
            severity = st.select_slider("Tamaño estimado", options=["Pequeño", "Mediano", "Grande"])
            reporter = st.text_input("Nombre (opcional)")
        confirmed = st.checkbox("Confirmo que la foto corresponde a una acumulación de basura")
        submitted = st.form_submit_button("Enviar reporte", type="primary")

    if submitted:
        if not photo:
            st.error("Adjunta una fotografía para enviar el reporte.")
        elif not confirmed:
            st.error("Confirma que la imagen muestra una acumulación de basura.")
        else:
            now = datetime.now().astimezone()
            image_dir = DATA_DIR / "photos"
            image_dir.mkdir(exist_ok=True)
            image_name = f"{now.strftime('%Y%m%d%H%M%S%f')}_{Path(photo.name).name}"
            (image_dir / image_name).write_bytes(photo.getvalue())
            report = {
                "id": now.strftime("CL-%Y%m%d%H%M%S%f"),
                "created_at": now.isoformat(timespec="seconds"),
                "category": category,
                "description": description.strip(),
                "neighborhood": neighborhood.strip(),
                "latitude": float(latitude),
                "longitude": float(longitude),
                "severity": severity,
                "reporter": reporter.strip() or "Anónimo",
                "status": "Pendiente",
                "photo": str(Path("data") / "photos" / image_name),
            }
            reports.append(report)
            save_reports(reports)
            st.success(f"Reporte registrado: {report['id']}")
            st.rerun()

with map_tab:
    st.subheader("Zonas reportadas")
    if reports:
        import pandas as pd
        points = pd.DataFrame([{"lat": r["latitude"], "lon": r["longitude"]} for r in reports])
        st.map(points, latitude="lat", longitude="lon", use_container_width=True)
        st.caption(f"{len(reports)} reporte(s) registrados. Los marcadores representan las coordenadas ingresadas por la comunidad.")
        st.dataframe(
            [{"ID": r["id"], "Fecha": r["created_at"], "Categoría": r["category"], "Barrio": r["neighborhood"], "Tamaño": r["severity"], "Estado": r["status"]} for r in reversed(reports)],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.write("Aún no hay reportes. Sé la primera persona en registrar un punto.")

with municipal_tab:
    st.subheader("Reportes para gestión municipal")
    st.caption("Vista básica para priorizar y descargar los reportes comunitarios.")
    if reports:
        pending = sum(1 for r in reports if r["status"] == "Pendiente")
        a, b, c = st.columns(3)
        a.metric("Reportes totales", len(reports))
        b.metric("Pendientes", pending)
        c.metric("Zonas", len({(r["latitude"], r["longitude"]) for r in reports}))
        output = io.StringIO()
        fields = ["id", "created_at", "category", "description", "neighborhood", "latitude", "longitude", "severity", "reporter", "status", "photo"]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(reports)
        st.download_button("Descargar reportes CSV", output.getvalue().encode("utf-8-sig"), "reportes_ciudad_limpia.csv", "text/csv")
        selected_id = st.selectbox("Actualizar estado de un reporte", [r["id"] for r in reports])
        new_status = st.selectbox("Estado", ["Pendiente", "En revisión", "Atendido"], key="status")
        if st.button("Guardar estado"):
            for item in reports:
                if item["id"] == selected_id:
                    item["status"] = new_status
                    break
            save_reports(reports)
            st.success("Estado actualizado.")
            st.rerun()
        with st.expander("Ver reportes con fotografía"):
            for item in reversed(reports):
                st.markdown(f"**{item['id']} · {item['category']} · {item['status']}** — {item['neighborhood'] or 'Sin referencia'}")
                image_path = Path(__file__).parent / item["photo"]
                if image_path.exists():
                    st.image(str(image_path), width=320)
                if item["description"]:
                    st.write(item["description"])
    else:
        st.write("Todavía no hay datos para mostrar.")

st.divider()
st.caption("Prototipo educativo. Antes de un despliegue municipal real, configura almacenamiento persistente, controles de acceso, moderación y política de privacidad.")
