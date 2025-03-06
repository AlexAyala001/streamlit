import pandas as pd
import polars as pl
import streamlit as st
from pathlib import Path
import os
import altair as alt

# Cargar los datos
df1 = pl.read_parquet("ctas_busqueda_fiserv.parquet")
df2 = pl.read_parquet("totales_ctas_busqueda_fiserv.parquet")
df3 = pd.read_csv("activas_con_oferta_con_compra.csv", dtype={'cuenta':str, 'no_fiserv__c':str,'estatus_slf':str})

# Función para contar ofertas
def count_ofertas(df, columna):
    return df[columna][-1]

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

    st.header("Configuración del gráfico")
    eje_y_opcion = st.selectbox(
        "Selecciona la métrica para graficar",
        [
            "Total_cuentas",
            "Activas_fiserv",
            "Activas_fiserv_oferta",
            "Activas_fiserv_oferta_compra",
            "Dinero_activas_fiserv_compra",
            "Activas_fiserv_estatus_Z"
        ],
        index=4  # Puedes poner por defecto "Dinero_activas_fiserv_compra"
    )


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
col1, col2, col3, col4, col5=st.columns(5)

with col1:
    st.metric(label="Total cuentas", value=f"{count_ofertas(df2, 'Total_cuentas'):,}")

with col2:
    st.metric(label="Activas fiserv", value=f"{count_ofertas(df2, 'Activas_fiserv'):,}")

with col3:
    st.metric(label="Activas con oferta", value=f"{count_ofertas(df2, 'Activas_fiserv_oferta'):,}")

with col4:
    st.metric(label="Activas con oferta y compra", value=f"{count_ofertas(df2, 'Activas_fiserv_oferta_compra'):,}")
    
with col5:
    st.metric(label="Dinero activas fiserv", value=f"${count_ofertas(df2, 'Dinero_activas_fiserv_compra'):,.2f}")

#with col6:
#    st.metric(label="Activas con estatus Z", value=f"{count_ofertas(df2, 'Activas_fiserv_estatus_Z'):,}")

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

    # Preparamos los datos para el gráfico
    grafico_df = df2.select(['info_day', eje_y_opcion]).to_pandas()
    
    # Asegurarse de que info_day sea tipo fecha si aplica
    grafico_df['info_day'] = pd.to_datetime(grafico_df['info_day'])

    # Calcular rango dinámico
    y_min = grafico_df[eje_y_opcion].min() * 0.99  # 10% debajo del mínimo
    y_max = grafico_df[eje_y_opcion].max() * 1.01  # 10% arriba del máximo

    # Crear gráfico dinámico de líneas con rango ajustado
    chart = alt.Chart(grafico_df).mark_line(point=True).encode(
        x=alt.X('info_day:T', title='Fecha'),
        y=alt.Y(
            f'{eje_y_opcion}:Q',
            title=eje_y_opcion.replace('_', ' '),
            scale=alt.Scale(domain=[y_min, y_max])
        ),
        tooltip=['info_day', eje_y_opcion]
    ).properties(
        title=f"{eje_y_opcion.replace('_', ' ')} a lo largo del tiempo",
        width=800,
        height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
    # Mostramos el DataFrame
    display_df = df3
    display_df_pandas = display_df

    # Centrar la tabla
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st.dataframe(display_df_pandas.head(10))
    st.markdown("</div>", unsafe_allow_html=True)

    # Botón para descargar archivo parquet
    with open("activas_con_oferta_con_compra.csv", "rb") as file:
        st.download_button(
            label="Descargar archivo CSV",
            data=file,
            file_name="activas_con_oferta_con_compra.csv",
            mime="application/octet-stream"
        )

    st.write("Aquí puedes agregar gráficos adicionales")

# Ejecutar la aplicación con 'streamlit run nombre_del_archivo.py'
