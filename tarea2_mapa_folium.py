"""
tarea2_mapa_folium.py
=====================
Pipeline ETL – Fase 3: Visualización interactiva con Folium
Viaje apostólico de León XIV a Canarias · 11–12 junio 2026

Requisitos:  pip install folium geopandas
Entrada:     agenda_papa · cortes_trafico · guaguas_impacto · aparcamientos (.geojson)
Salida:      index.html
"""

import folium
from folium import plugins
import geopandas as gpd

# ─────────────────────────────────────────────────────────────────────────────
# 1. HORAS (geopandas descarta campos time al leer GeoJSON; las reinyectamos)
# ─────────────────────────────────────────────────────────────────────────────

HORAS_AGENDA = {
    "A01": ("10:50", "11:00"), "A02": ("11:40", "12:25"),
    "A03": ("13:30", "14:30"), "A04": ("14:00", "18:30"),
    "A05": ("18:30", "20:00"), "A06": ("09:10", "09:30"),
    "A07": ("09:30", "10:00"), "A08": ("10:10", "11:30"),
    "A09": ("12:15", "14:00"), "A10": ("14:30", "15:00"),
}
HORAS_CORTES = {
    "C01": ("12:00", "13:30"), "C02": ("17:30", "18:30"), "C03": ("09:00", "23:59"),
}
HORAS_GUAGUAS = {
    "G01": ("14:00", "23:00"), "G02": ("14:00", "23:00"), "G03": ("14:00", "23:00"),
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. CARGA
# ─────────────────────────────────────────────────────────────────────────────

gdf_agenda  = gpd.read_file("agenda_papa.geojson")
gdf_cortes  = gpd.read_file("cortes_trafico.geojson")
gdf_guaguas = gpd.read_file("guaguas_impacto.geojson")
gdf_park    = gpd.read_file("aparcamientos.geojson")

gdf_agenda["hora_inicio"]  = gdf_agenda["id"].map(lambda x: HORAS_AGENDA.get(x, ("",""))[0])
gdf_agenda["hora_fin"]     = gdf_agenda["id"].map(lambda x: HORAS_AGENDA.get(x, ("",""))[1])
gdf_cortes["hora_inicio"]  = gdf_cortes["id"].map(lambda x: HORAS_CORTES.get(x, ("",""))[0])
gdf_cortes["hora_fin"]     = gdf_cortes["id"].map(lambda x: HORAS_CORTES.get(x, ("",""))[1])
gdf_guaguas["hora_inicio"] = gdf_guaguas["id"].map(lambda x: HORAS_GUAGUAS.get(x, ("",""))[0])
gdf_guaguas["hora_fin"]    = gdf_guaguas["id"].map(lambda x: HORAS_GUAGUAS.get(x, ("",""))[1])

print(f"  Agenda: {len(gdf_agenda)} · Cortes: {len(gdf_cortes)} · "
      f"Guaguas: {len(gdf_guaguas)} · Aparcamientos: {len(gdf_park)}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. MAPA BASE
# ─────────────────────────────────────────────────────────────────────────────

mapa = folium.Map(location=[28.10, -15.80], zoom_start=9,
                  tiles="CartoDB positron", prefer_canvas=True)

COLOR_IMPACTO = {"Alto": "#E24B4A", "Medio": "#EF9F27", "Bajo": "#639922"}
EVENTOS_TENERIFE = ("A06", "A07", "A08", "A09", "A10")

# ─────────────────────────────────────────────────────────────────────────────
# 4. POPUPS
# ─────────────────────────────────────────────────────────────────────────────

def popup_evento(row):
    color = COLOR_IMPACTO.get(row.tipo_impacto, "#888")
    isla = "Tenerife" if row.id in EVENTOS_TENERIFE else "Gran Canaria"
    html = f"""
    <div style="font-family:-apple-system,'Segoe UI',sans-serif;width:280px;border-radius:10px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.18);">
      <div style="background:{color};padding:10px 14px;">
        <span style="display:inline-block;background:rgba(255,255,255,0.25);color:#fff;font-size:10px;font-weight:600;letter-spacing:.8px;padding:2px 7px;border-radius:20px;text-transform:uppercase;">{row.tipo_impacto} · {isla}</span>
        <p style="margin:6px 0 0;color:#fff;font-size:14px;font-weight:600;line-height:1.3;">{row.evento}</p>
      </div>
      <div style="background:#fff;padding:10px 14px;">
        <p style="margin:0 0 6px;font-size:12px;color:#555;">📅 {row.fecha} &nbsp;·&nbsp; 🕐 {row.hora_inicio} – {row.hora_fin}</p>
        <p style="margin:0 0 8px;font-size:12px;color:#333;">📍 {row.lugar_texto}</p>
        <div style="background:#f5f5f5;border-left:3px solid {color};padding:7px 10px;border-radius:0 6px 6px 0;font-size:12px;color:#444;">💡 <strong>Consejo:</strong> {row.consejo_movilidad}</div>
      </div>
    </div>"""
    return folium.Popup(folium.IFrame(html, width=300, height=230), max_width=310)


def popup_guagua(row):
    html = f"""
    <div style="font-family:-apple-system,'Segoe UI',sans-serif;width:260px;border-radius:10px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);">
      <div style="background:#185FA5;padding:9px 13px;"><span style="color:#fff;font-size:13px;font-weight:600;">🚌 {row.tipo}</span></div>
      <div style="background:#fff;padding:9px 13px;">
        <p style="margin:0 0 5px;font-size:12px;font-weight:600;color:#222;">{row.descripcion}</p>
        <p style="margin:0 0 5px;font-size:11px;color:#555;">📅 {row.fecha} · {row.hora_inicio}–{row.hora_fin}</p>
        <div style="background:#eef4fb;border-left:3px solid #185FA5;padding:6px 9px;border-radius:0 5px 5px 0;font-size:11px;color:#333;">{row.alternativa}</div>
      </div>
    </div>"""
    return folium.Popup(folium.IFrame(html, width=275, height=170), max_width=285)


def popup_park(row):
    plazas_fmt = f"{int(row.plazas):,}".replace(",", ".")
    html = f"""
    <div style="font-family:-apple-system,'Segoe UI',sans-serif;width:250px;border-radius:10px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.15);">
      <div style="background:#2E7D32;padding:9px 13px;"><span style="color:#fff;font-size:13px;font-weight:600;">🅿️ {row.nombre}</span></div>
      <div style="background:#fff;padding:9px 13px;">
        <p style="margin:0 0 5px;font-size:20px;font-weight:700;color:#2E7D32;">{plazas_fmt} <span style="font-size:12px;font-weight:400;color:#555;">plazas</span></p>
        <div style="background:#FFF3E0;border-left:3px solid #EF6C00;padding:6px 9px;border-radius:0 5px 5px 0;font-size:11px;color:#5D4037;">⚠️ {row.requisito}</div>
      </div>
    </div>"""
    return folium.Popup(folium.IFrame(html, width=265, height=150), max_width=275)


# ─────────────────────────────────────────────────────────────────────────────
# 5. CAPA AGENDA
# ─────────────────────────────────────────────────────────────────────────────

cluster = plugins.MarkerCluster(name="🕊️ Agenda papal", show=True)
for _, row in gdf_agenda.iterrows():
    if row.geometry is None:
        continue
    color = COLOR_IMPACTO.get(row.tipo_impacto, "#888")
    icono = folium.DivIcon(
        html=f'<div style="width:32px;height:32px;border-radius:50%;background:{color};border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;font-size:14px;">🕊️</div>',
        icon_size=(32, 32), icon_anchor=(16, 16))
    folium.Marker([row.geometry.y, row.geometry.x], icon=icono,
                  popup=popup_evento(row),
                  tooltip=f"<b>{row.evento}</b><br>{row.hora_inicio}–{row.hora_fin}").add_to(cluster)
cluster.add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 6. CAPA CORTES
# ─────────────────────────────────────────────────────────────────────────────

capa_cortes = folium.FeatureGroup(name="🔴 Cortes de tráfico", show=True)
for _, row in gdf_cortes.iterrows():
    coords = [(lat, lon) for lon, lat in row.geometry.coords]
    folium.PolyLine(coords, color="#E24B4A", weight=6, opacity=0.85,
                    tooltip=f"<b>{row.descripcion}</b><br>{row.hora_inicio}–{row.hora_fin}",
                    popup=folium.Popup(f"<b>{row.descripcion}</b><br>📅 {row.fecha} · {row.hora_inicio}–{row.hora_fin}<br>🛣️ {row.via} · {row.tramo}", max_width=250)).add_to(capa_cortes)
capa_cortes.add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 7. CAPA GUAGUAS
# ─────────────────────────────────────────────────────────────────────────────

capa_guaguas = folium.FeatureGroup(name="🚌 Lanzaderas de guaguas", show=True)
for _, row in gdf_guaguas.iterrows():
    if row.geometry is None:
        continue
    icono = folium.DivIcon(
        html='<div style="width:28px;height:28px;border-radius:6px;background:#185FA5;border:2px solid #fff;box-shadow:0 2px 5px rgba(0,0,0,0.25);display:flex;align-items:center;justify-content:center;font-size:13px;">🚌</div>',
        icon_size=(28, 28), icon_anchor=(14, 14))
    folium.Marker([row.geometry.y, row.geometry.x], icon=icono,
                  popup=popup_guagua(row),
                  tooltip=f"<b>Lanzadera</b><br>{row.descripcion[:40]}…").add_to(capa_guaguas)
capa_guaguas.add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 8. CAPA APARCAMIENTOS
# ─────────────────────────────────────────────────────────────────────────────

capa_park = folium.FeatureGroup(name="🅿️ Aparcamientos habilitados", show=True)
for _, row in gdf_park.iterrows():
    if row.geometry is None:
        continue
    icono = folium.DivIcon(
        html='<div style="width:30px;height:30px;border-radius:6px;background:#2E7D32;border:2px solid #fff;box-shadow:0 2px 5px rgba(0,0,0,0.25);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:#fff;">P</div>',
        icon_size=(30, 30), icon_anchor=(15, 15))
    folium.Marker([row.geometry.y, row.geometry.x], icon=icono,
                  popup=popup_park(row),
                  tooltip=f"<b>{row.nombre}</b><br>{int(row.plazas)} plazas").add_to(capa_park)
capa_park.add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 9. CONTROLES
# ─────────────────────────────────────────────────────────────────────────────

folium.LayerControl(position="topright", collapsed=False).add_to(mapa)
plugins.MiniMap(toggle_display=True, position="bottomleft").add_to(mapa)
plugins.Fullscreen(position="topleft").add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 10. TÍTULO + LEYENDA
# ─────────────────────────────────────────────────────────────────────────────

TITULO_HTML = """
<div id="titulo-mapa" style="position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:9999;pointer-events:none;background:rgba(255,255,255,0.95);border-radius:10px;padding:10px 20px;box-shadow:0 2px 12px rgba(0,0,0,0.15);text-align:center;max-width:90vw;">
  <p style="margin:0;font-size:16px;font-weight:700;color:#222;font-family:-apple-system,sans-serif;">🕊️ León XIV en Canarias 2026 · Impacto en la movilidad</p>
  <p style="margin:3px 0 0;font-size:12px;color:#666;">Gran Canaria (11 jun) · Tenerife (12 jun) · Toca los marcadores</p>
</div>"""

LEYENDA_HTML = """
<div id="leyenda" style="position:fixed;bottom:30px;right:12px;z-index:9999;background:rgba(255,255,255,0.95);border-radius:10px;padding:12px 16px;box-shadow:0 2px 10px rgba(0,0,0,0.15);font-family:-apple-system,sans-serif;font-size:12px;color:#333;min-width:175px;">
  <p style="margin:0 0 8px;font-weight:700;font-size:13px;">Leyenda</p>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;"><span style="width:14px;height:14px;border-radius:50%;background:#E24B4A;border:2px solid #fff;flex-shrink:0;"></span>Acto · impacto alto</div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;"><span style="width:14px;height:14px;border-radius:50%;background:#EF9F27;border:2px solid #fff;flex-shrink:0;"></span>Acto · impacto medio</div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;"><span style="display:inline-block;width:28px;height:5px;background:#E24B4A;border-radius:3px;flex-shrink:0;"></span>Corte de tráfico</div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;"><span style="width:14px;height:14px;border-radius:3px;background:#185FA5;border:2px solid #fff;flex-shrink:0;"></span>Lanzadera de guagua</div>
  <div style="display:flex;align-items:center;gap:8px;"><span style="width:14px;height:14px;border-radius:3px;background:#2E7D32;border:2px solid #fff;flex-shrink:0;"></span>Aparcamiento (mín. 4 pers.)</div>
</div>"""

mapa.get_root().html.add_child(folium.Element(TITULO_HTML))
mapa.get_root().html.add_child(folium.Element(LEYENDA_HTML))

META_HTML = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta property="og:title" content="León XIV en Canarias 2026 – Mapa de impacto en la movilidad">
<meta property="og:description" content="Cortes de tráfico, guaguas especiales, aparcamientos y consejos para la visita papal a Gran Canaria y Tenerife.">
<style></style>"""

# ─────────────────────────────────────────────────────────────────────────────
# 11. EXPORTAR
# ─────────────────────────────────────────────────────────────────────────────

mapa.save("index.html")
print("═" * 60)
print("  ✓ index.html generado con la agenda oficial corregida.")
print("  → Abre index.html o súbelo a GitHub.")
print("═" * 60)
