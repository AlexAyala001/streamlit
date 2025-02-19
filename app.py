import pandas as pd
import polars as pl
import streamlit as st
from pathlib import Path
import os

# Cargar los datos
df1 = pl.read_parquet("ctas_busqueda_fiserv.parquet")
df2 = pl.read_parquet("totales_ctas_busqueda_fiserv.parquet")

# Función para contar ofertas
def count_ofertas(df, columna):
    return df[columna][0]

# Configuración de la página de Streamlit
st.set_page_config(page_title="Reporte Crédito Revolvente", layout="wide")
st.title("Reporte Crédito Revolvente")

# Sidebar para filtros interactivos
with st.sidebar:
    st.header("Filtros de búsqueda")
    cuenta = st.text_input("Número de Cuenta", placeholder="Busca por número de cuenta", key="cuenta_input")
    fiserv = st.text_input("Número Fiserv", placeholder="Busca por número fiserv", key="fiserv_input")

# Filtro de DataFrame
def filtrado1_df():
    if cuenta:
        filt_df = df1.filter(pl.col("idcuentabrm__c") == cuenta)
    elif fiserv:
        filt_df = df1.filter(pl.col("no_fiserv__c") == fiserv)
    else:
        filt_df = df1
    return filt_df

# Mostrar métricas
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total cuentas", value=f"{count_ofertas(df2, 'Total_cuentas'):,}")

with col2:
    st.metric(label="Activas fiserv", value=f"{count_ofertas(df2, 'Activas_fiserv'):,}")

with col3:
    st.metric(label="Distintas a Activo", value=f"{count_ofertas(df2, 'Distintas_Activo'):,}")

# Tabs para el resumen
tab1, tab2 = st.tabs(["Tabla Histórico", "Gráficos"])

with tab1:
    st.write("Tabla Histórico")

    display_df = filtrado1_df().select(['idcuentabrm__c', 'no_fiserv__c','id', 'estatus__c', 'entidad__c', 'lastmodifieddate', 'createddate', 'no_tarjeta_dumi__c', 'partition_0'])
    display_df_pandas = display_df.to_pandas()

    # Centrar la tabla
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.dataframe(display_df_pandas.head(12))
    st.markdown("</div>", unsafe_allow_html=True)

    # Botón para descargar archivo parquet
    with open("ctas_busqueda_fiserv.parquet", "rb") as file:
        st.download_button(
            label="Descargar archivo Parquet",
            data=file,
            file_name="ctas_busqueda_fiserv.parquet",
            mime="application/octet-stream"
        )

#with tab2:
#    st.write("Gráficos")
#    st.write("Aquí puedes agregar gráficos adicionales")

# Ejecutar la aplicación con 'streamlit run nombre_del_archivo.py'
