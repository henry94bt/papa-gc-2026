"""
tarea2_mapa_folium.py
=====================
Pipeline ETL – Fase 3: Visualización interactiva con Folium
Visita papal a Gran Canaria · 11–12 junio 2026

Requisitos:
    pip install folium geopandas

Entrada:  agenda_papa.geojson · cortes_trafico.geojson · guaguas_impacto.geojson
Salida:   index.html  (listo para GitHub Pages o cualquier hosting estático)

Uso:
    python tarea2_mapa_folium.py
    Abre index.html en el navegador.
"""

import json
import folium
from folium import plugins
import geopandas as gpd

# ─────────────────────────────────────────────────────────────────────────────
# 1. CARGA DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
# NOTA: geopandas descarta campos de tipo time al leer GeoJSON (OGR type 10).
# Solución: reinyectamos las horas desde dicts por ID.

HORAS_AGENDA = {
    "A01": ("10:00", "11:00"),
    "A02": ("12:00", "13:30"),
    "A03": ("13:30", "15:00"),
    "A04": ("18:00", "21:00"),
    "A05": ("10:00", "13:00"),
    "A06": ("16:00", "17:30"),
}
HORAS_CORTES = {
    "C01": ("08:00", "13:00"),
    "C02": ("07:00", "15:00"),
    "C03": ("10:00", "16:00"),
}
HORAS_GUAGUAS = {
    "G01": ("10:00", "16:00"),
    "G02": ("14:00", "23:00"),
    "G03": ("14:00", "23:00"),
    "G04": ("06:00", "16:00"),
}

gdf_agenda  = gpd.read_file("agenda_papa.geojson")
gdf_cortes  = gpd.read_file("cortes_trafico.geojson")
gdf_guaguas = gpd.read_file("guaguas_impacto.geojson")

gdf_agenda["hora_inicio"]  = gdf_agenda["id"].map(lambda x: HORAS_AGENDA.get(x, ("",""))[0])
gdf_agenda["hora_fin"]     = gdf_agenda["id"].map(lambda x: HORAS_AGENDA.get(x, ("",""))[1])
gdf_cortes["hora_inicio"]  = gdf_cortes["id"].map(lambda x: HORAS_CORTES.get(x, ("",""))[0])
gdf_cortes["hora_fin"]     = gdf_cortes["id"].map(lambda x: HORAS_CORTES.get(x, ("",""))[1])
gdf_guaguas["hora_inicio"] = gdf_guaguas["id"].map(lambda x: HORAS_GUAGUAS.get(x, ("",""))[0])
gdf_guaguas["hora_fin"]    = gdf_guaguas["id"].map(lambda x: HORAS_GUAGUAS.get(x, ("",""))[1])

print(f"  Agenda:  {len(gdf_agenda)} eventos")
print(f"  Cortes:  {len(gdf_cortes)} tramos")
print(f"  Guaguas: {len(gdf_guaguas)} paradas/intercambiadores")

# ─────────────────────────────────────────────────────────────────────────────
# 2. MAPA BASE
# ─────────────────────────────────────────────────────────────────────────────

mapa = folium.Map(
    location=[27.92, -15.54],   # Centro de Gran Canaria
    zoom_start=10,
    tiles="CartoDB positron",
    prefer_canvas=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# 3. FUNCIÓN: POPUP HTML ESTÉTICO
# ─────────────────────────────────────────────────────────────────────────────

COLOR_IMPACTO = {"Alto": "#E24B4A", "Medio": "#EF9F27", "Bajo": "#639922"}

def popup_evento(row) -> folium.Popup:
    color = COLOR_IMPACTO.get(row.tipo_impacto, "#888")
    html = f"""
    <div style="
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        width: 280px; padding: 0; border-radius: 10px; overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    ">
      <!-- Cabecera de color según impacto -->
      <div style="background:{color}; padding: 10px 14px;">
        <span style="
            display:inline-block; background:rgba(255,255,255,0.25);
            color:#fff; font-size:10px; font-weight:600; letter-spacing:.8px;
            padding:2px 7px; border-radius:20px; text-transform:uppercase;
        ">{row.tipo_impacto}</span>
        <p style="margin:6px 0 0; color:#fff; font-size:14px; font-weight:600;
                  line-height:1.3;">{row.evento}</p>
      </div>
      <!-- Cuerpo -->
      <div style="background:#fff; padding:10px 14px;">
        <p style="margin:0 0 6px; font-size:12px; color:#555;">
          📅 {row.fecha} &nbsp;·&nbsp; 🕐 {row.hora_inicio} – {row.hora_fin}
        </p>
        <p style="margin:0 0 8px; font-size:12px; color:#333;">
          📍 {row.lugar_texto}
        </p>
        <div style="background:#f5f5f5; border-left:3px solid {color};
                    padding:7px 10px; border-radius:0 6px 6px 0; font-size:12px; color:#444;">
          💡 <strong>Consejo:</strong> {row.consejo_movilidad}
        </div>
      </div>
    </div>
    """
    return folium.Popup(folium.IFrame(html, width=300, height=210), max_width=310)


def popup_guagua(row) -> folium.Popup:
    es_intercambiador = "provisional" in row.tipo.lower()
    color = "#185FA5" if es_intercambiador else "#A32D2D"
    icono  = "🔄" if es_intercambiador else "🚫"
    html = f"""
    <div style="
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        width: 270px; padding: 0; border-radius: 10px; overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    ">
      <div style="background:{color}; padding: 9px 13px;">
        <span style="color:#fff; font-size:13px; font-weight:600;">{icono} {row.tipo}</span>
      </div>
      <div style="background:#fff; padding:9px 13px;">
        <p style="margin:0 0 5px; font-size:12px; font-weight:600; color:#222;">{row.descripcion}</p>
        <p style="margin:0 0 5px; font-size:11px; color:#555;">
          📅 {row.fecha} &nbsp;·&nbsp; {row.hora_inicio} – {row.hora_fin}
        </p>
        <div style="background:#eef4fb; border-left:3px solid {color};
                    padding:6px 9px; border-radius:0 5px 5px 0; font-size:11px; color:#333;">
          {row.alternativa}
        </div>
      </div>
    </div>
    """
    return folium.Popup(folium.IFrame(html, width=285, height=190), max_width=295)


# ─────────────────────────────────────────────────────────────────────────────
# 4. CAPA: AGENDA PAPAL (marcadores con cluster)
# ─────────────────────────────────────────────────────────────────────────────

cluster_agenda = plugins.MarkerCluster(name="🕊️ Agenda papal", show=True)

for _, row in gdf_agenda.iterrows():
    if row.geometry is None:
        continue
    color = COLOR_IMPACTO.get(row.tipo_impacto, "#888")
    icono = folium.DivIcon(
        html=f"""
        <div style="
            width:32px; height:32px; border-radius:50%;
            background:{color}; border:3px solid #fff;
            box-shadow:0 2px 6px rgba(0,0,0,0.3);
            display:flex; align-items:center; justify-content:center;
            font-size:14px;
        ">🕊️</div>
        """,
        icon_size=(32, 32),
        icon_anchor=(16, 16),
    )
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        icon=icono,
        popup=popup_evento(row),
        tooltip=f"<b>{row.evento}</b><br>{row.hora_inicio} – {row.hora_fin}",
    ).add_to(cluster_agenda)

cluster_agenda.add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 5. CAPA: CORTES DE TRÁFICO (líneas rojas)
# ─────────────────────────────────────────────────────────────────────────────

capa_cortes = folium.FeatureGroup(name="🔴 Cortes de tráfico", show=True)

for _, row in gdf_cortes.iterrows():
    coords_leaflet = [(lat, lon) for lon, lat in row.geometry.coords]
    folium.PolyLine(
        locations=coords_leaflet,
        color="#E24B4A",
        weight=6,
        opacity=0.85,
        tooltip=f"<b>{row.descripcion}</b><br>{row.hora_inicio}–{row.hora_fin}",
        popup=folium.Popup(
            f"<b>{row.descripcion}</b><br>"
            f"📅 {row.fecha} · {row.hora_inicio}–{row.hora_fin}<br>"
            f"🛣️ {row.via} · {row.tramo}",
            max_width=250,
        ),
    ).add_to(capa_cortes)

    # Flechas de dirección a lo largo de la línea
    plugins.PolyLineTextPath(
        folium.PolyLine(locations=coords_leaflet, opacity=0),
        "►",
        repeat=True,
        offset=14,
        attributes={"fill": "#E24B4A", "font-size": "12", "font-weight": "bold"},
    ).add_to(capa_cortes)

capa_cortes.add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 6. CAPA: GUAGUAS (paradas inhabilitadas + intercambiadores)
# ─────────────────────────────────────────────────────────────────────────────

capa_guaguas = folium.FeatureGroup(name="🚌 Guaguas – impacto", show=True)

for _, row in gdf_guaguas.iterrows():
    if row.geometry is None:
        continue
    es_intercambiador = "provisional" in row.tipo.lower()
    color  = "#185FA5" if es_intercambiador else "#A32D2D"
    emoji  = "🔄" if es_intercambiador else "🚫"
    icono = folium.DivIcon(
        html=f"""
        <div style="
            width:28px; height:28px; border-radius:6px;
            background:{color}; border:2px solid #fff;
            box-shadow:0 2px 5px rgba(0,0,0,0.25);
            display:flex; align-items:center; justify-content:center;
            font-size:13px;
        ">{emoji}</div>
        """,
        icon_size=(28, 28),
        icon_anchor=(14, 14),
    )
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        icon=icono,
        popup=popup_guagua(row),
        tooltip=f"<b>{row.tipo}</b><br>{row.descripcion[:40]}…",
    ).add_to(capa_guaguas)

capa_guaguas.add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 7. CONTROLES DEL MAPA
# ─────────────────────────────────────────────────────────────────────────────

# Control de capas (toggle en esquina superior derecha)
folium.LayerControl(position="topright", collapsed=False).add_to(mapa)

# Minimap en esquina inferior izquierda
plugins.MiniMap(toggle_display=True, position="bottomleft").add_to(mapa)

# Escala
folium.plugins.MousePosition().add_to(mapa)
folium.plugins.Fullscreen(position="topleft").add_to(mapa)

# ─────────────────────────────────────────────────────────────────────────────
# 8. LEYENDA Y TÍTULO (HTML custom inyectado en el mapa)
# ─────────────────────────────────────────────────────────────────────────────

TITULO_HTML = """
<div id="titulo-mapa" style="
    position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
    z-index: 9999; pointer-events: none;
    background: rgba(255,255,255,0.95);
    border-radius: 10px; padding: 10px 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    text-align: center; max-width: 90vw;
">
  <p style="margin:0; font-size:16px; font-weight:700; color:#222;
             font-family: -apple-system, sans-serif;">
    🕊️ Papa en Canarias 2026 · Impacto en la movilidad
  </p>
  <p style="margin:3px 0 0; font-size:12px; color:#666;">
    Gran Canaria · 11–12 junio 2026 · Toca los marcadores para ver consejos
  </p>
</div>
"""

LEYENDA_HTML = """
<div id="leyenda" style="
    position: fixed; bottom: 30px; right: 12px; z-index: 9999;
    background: rgba(255,255,255,0.95); border-radius: 10px;
    padding: 12px 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    font-family: -apple-system, sans-serif; font-size: 12px; color: #333;
    min-width: 170px;
">
  <p style="margin:0 0 8px; font-weight:700; font-size:13px;">Leyenda</p>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
    <span style="width:14px;height:14px;border-radius:50%;background:#E24B4A;
                 border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,0.2);
                 flex-shrink:0;"></span>
    Impacto Alto
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
    <span style="width:14px;height:14px;border-radius:50%;background:#EF9F27;
                 border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,0.2);
                 flex-shrink:0;"></span>
    Impacto Medio
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
    <span style="display:inline-block;width:28px;height:5px;
                 background:#E24B4A;border-radius:3px;flex-shrink:0;"></span>
    Corte de tráfico
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
    <span style="width:14px;height:14px;border-radius:3px;background:#185FA5;
                 border:2px solid #fff;flex-shrink:0;"></span>
    Intercambiador P+R
  </div>
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="width:14px;height:14px;border-radius:3px;background:#A32D2D;
                 border:2px solid #fff;flex-shrink:0;"></span>
    Parada inhabilitada
  </div>
</div>
"""

mapa.get_root().html.add_child(folium.Element(TITULO_HTML))
mapa.get_root().html.add_child(folium.Element(LEYENDA_HTML))

# ─────────────────────────────────────────────────────────────────────────────
# 9. META TAGS MOBILE-FIRST (para que WhatsApp/Twitter lo abra bien)
# ─────────────────────────────────────────────────────────────────────────────

META_HTML = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta property="og:title" content="🕊️ Papa en Canarias 2026 – Mapa de impacto en la movilidad">
<meta property="og:description"
      content="¿Cómo afecta la visita papal a tu desplazamiento en Gran Canaria? Cortes de tráfico, guaguas especiales y consejos en tiempo real.">
<meta property="og:image" content="https://TU_USUARIO.github.io/papa-gc-2026/preview.jpg">
<meta name="twitter:card" content="summary_large_image">
<style>
  /* Mobile: ocultar título si la pantalla es muy pequeña */
  @media (max-width: 500px) {
    #titulo-mapa { top: 6px; padding: 7px 14px; }
    #titulo-mapa p:first-child { font-size: 13px; }
    #titulo-mapa p:last-child { display: none; }
    #leyenda { font-size: 11px; padding: 9px 12px; bottom: 20px; }
  }
</style>
"""

mapa.get_root().header.add_child(folium.Element(META_HTML))

# ─────────────────────────────────────────────────────────────────────────────
# 10. EXPORTAR
# ─────────────────────────────────────────────────────────────────────────────

mapa.save("index.html")

print("═" * 60)
print("  ✓ index.html generado correctamente.")
print("  → Abre index.html en tu navegador para ver el mapa.")
print("  → Sube la carpeta a GitHub Pages para publicarlo.")
print("═" * 60)
