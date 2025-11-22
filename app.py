import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image



# ----------------------------------------------------------
# CONFIGURACIÓN GENERAL DE LA APP
# ----------------------------------------------------------

st.set_page_config(
    page_title="Asignación de Turnos de Enfermería",
    layout="wide",
    page_icon="🧑‍⚕️",
    initial_sidebar_state="expanded"
)

# Logo institucional (puedes cambiar el archivo por el logo de tu hospital)
col_logo, col_title = st.columns([2, 5])
with col_logo:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=700)
    except:
        st.write(":hospital:")
with col_title:
    st.title("" 
    "Gestión Profesional de Turnos de Enfermería")
    st.markdown("""
    <span style='font-size:18px;'>
    Bienvenido al sistema avanzado de visualización y análisis de turnos.<br>
    <ul>
    <li>Visualiza la asignación de personal por turno</li>
    <li>Detecta desequilibrios y sobrecargas</li>
    <li>Recibe recomendaciones automáticas</li>
    </ul>
    </span>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------
# CARGA DE DATOS DESDE EL EXCEL GENERADO EN MATLAB
# ----------------------------------------------------------

try:
    df = pd.read_excel("Solucions.xlsx", header=None)
except:
    st.error("❌ No se encontró el archivo 'Solucions.xlsx'. Asegúrate de colocarlo en la misma carpeta del app.py.")
    st.stop()

df.index = [f"Enfermera {i+1}" for i in range(df.shape[0])]
df.columns = [f"Turno {j+1}" for j in range(df.shape[1])]

# Convertimos 0 y 1 en etiquetas visuales amigables
df_visual = df.replace({1: "🟩 Trabaja", 0: "⬜ Descansa"})

# ----------------------------------------------------------
# VISTA GENERAL
# ----------------------------------------------------------

st.header("📅 Vista general de horarios")
st.markdown("""
<span style='font-size:16px;'>
Cada fila representa una enfermera y cada columna un turno.<br>
El color indica si trabaja (<span style='color:green;'>🟩</span>) o descansa (<span style='color:gray;'>⬜</span>).
</span>
""", unsafe_allow_html=True)
st.dataframe(df_visual, height=400, use_container_width=True)

# ----------------------------------------------------------
# VISTA POR ENFERMERA
# ----------------------------------------------------------

st.header("👩‍⚕️ Horario individual por enfermera")
with st.expander("Ver detalle por enfermera", expanded=True):
    selected = st.selectbox("Selecciona una enfermera:", df_visual.index)
    colA, colB, colC = st.columns(3)
    with colA:
        btn_trabaja = st.button("Trabaja", key=f"trabaja_{selected}")
    with colB:
        btn_descansa = st.button("Descansa", key=f"descansa_{selected}")
    with colC:
        btn_todos = st.button("Todos", key=f"todos_{selected}")

    # Estado del filtro
    if btn_trabaja:
        filtro = "Trabaja"
    elif btn_descansa:
        filtro = "Descansa"
    else:
        filtro = "Todos"

    st.subheader(f"Horario de {selected}")
    horario = df_visual.loc[[selected]].T.copy()
    if filtro == "Trabaja":
        horario = horario[horario[selected] == "🟩 Trabaja"]
    elif filtro == "Descansa":
        horario = horario[horario[selected] == "⬜ Descansa"]
    st.table(horario)

    # Contadores interactivos
    turnos_trabajados = int(df.loc[selected].sum())
    turnos_descansados = int((df.shape[1]) - turnos_trabajados)
    if filtro == "Trabaja":
        st.metric(label="Turnos trabajados", value=turnos_trabajados)
    elif filtro == "Descansa":
        st.metric(label="Turnos descansados", value=turnos_descansados)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Turnos trabajados", value=turnos_trabajados)
        with col2:
            st.metric(label="Turnos descansados", value=turnos_descansados)

# ----------------------------------------------------------
# GRÁFICO: ENFERMERAS POR TURNO
# ----------------------------------------------------------

enfermeras_por_turno = df.sum(axis=0)
st.header("👥 Cantidad de enfermeras por turno")
enfermeras_por_turno = df.sum(axis=0)
fig1 = px.bar(
    enfermeras_por_turno,
    labels={'index':'Turno', 'value':'Cantidad de enfermeras'},
    title="Número de enfermeras asignadas en cada turno",
    color=enfermeras_por_turno,
    color_continuous_scale='Blues'
)
st.plotly_chart(fig1, use_container_width=True)

# ----------------------------------------------------------
# RECOMENDACIONES AUTOMÁTICAS
# ----------------------------------------------------------

st.header("📝 Recomendaciones Automáticas")
min_cobertura = enfermeras_por_turno.min()
max_carga = df.sum(axis=1).max()
turnos_criticos = enfermeras_por_turno[enfermeras_por_turno == min_cobertura].index.tolist()
enfermeras_cargadas = df.sum(axis=1)[df.sum(axis=1) == max_carga].index.tolist()

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔴 Turnos con baja cobertura")
    st.write(f"<b>{min_cobertura}</b> enfermeras en: <span style='color:red'>{', '.join(turnos_criticos)}</span>", unsafe_allow_html=True)
with col2:
    st.subheader("🟡 Enfermeras con mayor carga laboral")
    st.write(f"<b>{max_carga}</b> turnos: <span style='color:orange'>{', '.join(enfermeras_cargadas)}</span>", unsafe_allow_html=True)

with st.expander("Interpretación y recomendaciones", expanded=True):
    st.markdown(
        "<ul>"
        "<li><b>Turnos con baja cobertura:</b> Revisar estos turnos para evitar riesgos operativos y sobrecarga.</li>"
        "<li><b>Enfermeras con mayor carga laboral:</b> Redistribuir turnos para mejorar el equilibrio y evitar fatiga.</li>"
        "</ul>"
        "<span style='color:green;'>Esta información permite tomar decisiones informadas para mejorar la calidad del servicio y la distribución de carga.</span>",
        unsafe_allow_html=True
    )
    