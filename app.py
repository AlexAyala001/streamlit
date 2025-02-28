import pandas as pd
import polars as pl
import streamlit as st
from pathlib import Path
import os

# Cargar los datos
df1 = pl.read_parquet("ctas_busqueda_fiserv.parquet")
df2 = pl.read_parquet("totales_ctas_busqueda_fiserv.parquet")
df3 = pl.read_parquet("activas_con_oferta_con_compra.parquet")

# Función para contar ofertas
def count_ofertas(df, columna):
    return df[columna][0]

# Configuración de la página de Streamlit
st.set_page_config(page_title="Reporte Crédito Revolvente", layout="wide")
st.title("Reporte Crédito Revolvente")

# Sidebar para filtros interactivos
with st.sidebar:
    st.header("Filtros de búsqueda")
    cuenta = st.text_input("Número de Cuenta (separar por comas)", placeholder="Busca por número de cuenta", key="cuenta_input")
    fiserv = st.text_input("Número Fiserv (separar por comas)", placeholder="Busca por número fiserv", key="fiserv_input")
    uploaded_file = st.file_uploader("Sube un archivo CSV con números de cuenta o fiserv", type=["csv"])

    cuentas_list = []
    fiserv_list = []

    if uploaded_file:
        df_uploaded = pd.read_csv(uploaded_file)
        if "idcuentabrm__c" in df_uploaded.columns:
            cuentas_list = df_uploaded["idcuentabrm__c"].astype(str).tolist()
        if "no_fiserv__c" in df_uploaded.columns:
            fiserv_list = df_uploaded["no_fiserv__c"].astype(str).tolist()

# Filtro de DataFrame
def filtrado1_df():
    filt_df = df1
    if cuenta:
        cuentas_list.extend([c.strip() for c in cuenta.split(',')])
    if fiserv:
        fiserv_list.extend([f.strip() for f in fiserv.split(',')])

    if cuentas_list:
        filt_df = filt_df.filter(pl.col("idcuentabrm__c").is_in(cuentas_list))
    if fiserv_list:
        filt_df = filt_df.filter(pl.col("no_fiserv__c").is_in(fiserv_list))
    return filt_df

# Mostrar métricas
col1, col2, col3, col4, col5 =st.columns(5)

with col1:
    st.metric(label="Total cuentas", value=f"{count_ofertas(df2, 'Total_cuentas'):,}")

with col2:
    st.metric(label="Activas fiserv", value=f"{count_ofertas(df2, 'Activas_fiserv'):,}")

with col3:
    st.metric(label="Distintas a Activo", value=f"{count_ofertas(df2, 'Distintas_Activo'):,}")

with col4:
    st.metric(label="Activas con oferta", value=f"{count_ofertas(df2, 'Activas_fiserv_oferta'):,}")

with col5:
    st.metric(label="Activas con oferta y compra", value=f"{count_ofertas(df2, 'Activas_fiserv_oferta_compra'):,}")

with col6:
    st.metric(label="Activas con estatus Z", value=f"{count_ofertas(df2, 'Activas_fiserv_estatus_Z'):,}")

# Tabs para el resumen
tab1, tab2 = st.tabs(["Crédito Revolvente", "Activas Fiserv"])

with tab1:
    st.write("Crédito Revolvente")

    display_df = filtrado1_df().select(['idcuentabrm__c', 'no_fiserv__c','id', 'estatus__c', 'entidad__c', 'lastmodifieddate', 'createddate', 'no_tarjeta_dumi__c', 'partition_0'])
    display_df_pandas = display_df.to_pandas()

    # Centrar la tabla
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.dataframe(display_df_pandas.head(10))
    st.markdown("</div>", unsafe_allow_html=True)

    # Botón para descargar archivo parquet
    with open("ctas_busqueda_fiserv.parquet", "rb") as file:
        st.download_button(
            label="Descargar archivo Parquet",
            data=file,
            file_name="ctas_busqueda_fiserv.parquet",
            mime="application/octet-stream"
        )

with tab2:
    st.write("Activas Fiserv con oferta y saldo actual mayor a 0")
    display_df = df3
    display_df_pandas = display_df.to_pandas()

    # Centrar la tabla
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.dataframe(display_df_pandas.head(10))
    st.markdown("</div>", unsafe_allow_html=True)

    # Botón para descargar archivo parquet
    with open("ctas_busqueda_fiserv.parquet", "rb") as file:
        st.download_button(
            label="Descargar archivo Parquet",
            data=file,
            file_name="activas_con_oferta_con_compra.parquet",
            mime="application/octet-stream"
        )
    st.write("Aquí puedes agregar gráficos adicionales")

# Ejecutar la aplicación con 'streamlit run nombre_del_archivo.py'
