import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2

# -----------------------------------------
# CONFIGURACIÓN
# -----------------------------------------
st.set_page_config(page_title="Dashboard Cáncer Infantil", layout="wide")
st.title("Dashboard de Cáncer Infantil en Risaralda")

# -----------------------------------------
# CARGAR DATOS DESDE CSV
# -----------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("Datos_Postgrade.csv", encoding="utf-8")
    return df

df = cargar_datos()

df["Ano"] = df["Ano"].str.replace(",", "").astype(int)

# Estándar: quitar espacios en nombres
df["Clasificacion del Cancer"] = df["Clasificacion del Cancer"].str.strip()

# Separar TOTAL y TIPOS reales
df_total = df[df["Clasificacion del Cancer"] == "Total"].copy()
df_tipos = df[df["Clasificacion del Cancer"] != "Total"].copy()

# Grupos de edad
grupos_edad = ["0-4 anos", "5-9 anos", "10-14 anos", "15-19 anos"]

# -----------------------------------------
# FILTROS
# -----------------------------------------
colA, colB = st.columns(2)

años = sorted(df["Ano"].unique())
tipos = sorted(df_tipos["Clasificacion del Cancer"].unique())

año_sel = colA.selectbox("Seleccionar Año:", años, index=len(años)-1)
tipo_sel = colB.multiselect("Seleccionar Tipo de Cáncer:", tipos, default=tipos)

# Filtrar
df_total_year = df_total[df_total["Ano"] == año_sel]
df_tipos_year = df_tipos[(df_tipos["Ano"] == año_sel) & (df_tipos["Clasificacion del Cancer"].isin(tipo_sel))]

# -----------------------------------------
# KPIs
# -----------------------------------------
# Total de casos = fila "Total"
total_casos = int(df_total_year["Total general"].values[0]) if not df_total_year.empty else 0

# Tipos con casos > 0
num_tipos = df_tipos_year[df_tipos_year["Total general"] > 0]["Clasificacion del Cancer"].nunique()

k1, k2 = st.columns(2)
k1.metric("Total de casos en el año", f"{total_casos}")
k2.metric("Tipos de cáncer con casos", f"{num_tipos}")

# -----------------------------------------
# GRÁFICA DE LÍNEA
# -----------------------------------------
st.subheader("Evolución histórica por tipo de cáncer seleccionado")

df_linea = df[df["Clasificacion del Cancer"].isin(tipo_sel)].copy()

# Convertir Año a string para evitar 2022.5 → pero conservamos orden numérico
df_linea = df_linea.sort_values("Ano")   # 🔥 Ordenar antes de convertir
df_linea["Ano"] = df_linea["Ano"].astype(str)

fig_linea = px.line(
    df_linea,
    x="Ano",
    y="Total general",
    color="Clasificacion del Cancer",
    markers=True,
    title="Evolución de casos en el tiempo"
)

fig_linea.update_layout(
    xaxis_title="Año",
    yaxis_title="Total de Casos",
    xaxis=dict(type="category")  # 🔥 Evita años con decimales
)

st.plotly_chart(fig_linea, use_container_width=True)




# -----------------------------------------
# GRÁFICAS EN DOS COLUMNAS
# -----------------------------------------
col1, col2 = st.columns(2)

# Barras
fig_bar = px.bar(
    df_tipos_year,
    x="Clasificacion del Cancer",
    y="Total general",
    title="Casos por tipo de cáncer",
    height=500
)
col1.plotly_chart(fig_bar, use_container_width=True)

# Barras apiladas
df_melt = df_tipos_year.melt(
    id_vars=["Clasificacion del Cancer"],
    value_vars=grupos_edad,
    var_name="Grupo Etario",
    value_name="Casos"
)

fig_stack = px.bar(
    df_melt,
    x="Clasificacion del Cancer",
    y="Casos",
    color="Grupo Etario",
    title="Distribución por grupos etarios",
    barmode="stack",
    height=500
)
col2.plotly_chart(fig_stack, use_container_width=True)

# -----------------------------------------
# TABLA FINAL
# -----------------------------------------
st.subheader("Datos filtrados")
st.dataframe(df_tipos_year, use_container_width=True)

