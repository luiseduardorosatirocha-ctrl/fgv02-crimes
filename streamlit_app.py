import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Crimes - FGV", layout="wide")

st.title("Análise de Crimes por Tipo e Estado - Ano 2024")
st.write(
    """
    Aplicativo desenvolvido na disciplina de Programação (FGV Direito) para análise de dados criminais.
    Os dados incluem **tipo de crime**, **estado**, **ano** e **número de registros**, com base
    em informações extraídas de painel público do Power BI.
    A partir desses dados, são gerados gráficos e um relatório sintético de tendências.
    """
)

@st.cache_data
def carregar_dados(caminho_csv: str) -> pd.DataFrame:
    df = pd.read_csv(caminho_csv)
    return df

CAMINHO_CSV = "crimes.csv"

try:
    df = carregar_dados(CAMINHO_CSV)
except FileNotFoundError:
    st.error(
        f"Arquivo `{CAMINHO_CSV}` não encontrado. "
        "Coloque o CSV com esse nome no mesmo repositório do aplicativo."
    )
    st.stop()

colunas_esperadas = ["tipo_crime", "estado", "ano", "registros"]
if not all(col in df.columns for col in colunas_esperadas):
    st.warning(
        "As colunas esperadas são: 'tipo_crime', 'estado', 'ano', 'registros'. "
        "Verifique se o CSV está com esses nomes."
    )

df["ano"] = df["ano"].astype(int)
df["registros"] = pd.to_numeric(df["registros"], errors="coerce").fillna(0)

st.sidebar.header("Filtros")

anos_disponiveis = sorted(df["ano"].unique())
ano_selecionado = st.sidebar.selectbox("Ano", anos_disponiveis, index=len(anos_disponiveis)-1)

estados_disponiveis = sorted(df["estado"].unique())
estados_selecionados = st.sidebar.multiselect(
    "Estados", estados_disponiveis, default=estados_disponiveis
)

tipos_disponiveis = sorted(df["tipo_crime"].unique())
tipos_selecionados = st.sidebar.multiselect(
    "Tipos de crime", tipos_disponiveis, default=tipos_disponiveis
)

df_filtrado = df.copy()
df_filtrado = df_filtrado[df_filtrado["ano"] == ano_selecionado]
df_filtrado = df_filtrado[df_filtrado["estado"].isin(estados_selecionados)]
df_filtrado = df_filtrado[df_filtrado["tipo_crime"].isin(tipos_selecionados)]

st.subheader("Dados filtrados")
st.dataframe(df_filtrado)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Quantidade de crimes por tipo")
    if not df_filtrado.empty:
        por_tipo = (
            df_filtrado.groupby("tipo_crime")["registros"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(por_tipo)
    else:
        st.info("Ajuste os filtros para visualizar dados.")

with col2:
    st.subheader("Quantidade de crimes por estado")
    if not df_filtrado.empty:
        por_estado = (
            df_filtrado.groupby("estado")["registros"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(por_estado)
    else:
        st.info("Ajuste os filtros para visualizar dados.")

st.subheader("Evolução temporal (total de crimes por ano)")
evolucao = df.groupby("ano")["registros"].sum().sort_index()
st.line_chart(evolucao)

st.subheader("Relatório de tendências (síntese automática)")

texto = []

total_geral = int(df["registros"].sum())
texto.append(
    f"- Total de registros na base: **{total_geral:,}** ocorrências (todas as categorias).".replace(",", ".")
)

tipo_top = df.groupby("tipo_crime")["registros"].sum().sort_values(ascending=False)
if not tipo_top.empty:
    texto.append(
        f"- O tipo de crime com maior número de registros é **{tipo_top.index[0]}**, "
        f"com **{int(tipo_top.iloc[0]):,}** ocorrências.".replace(",", ".")
    )

estado_top = df.groupby("estado")["registros"].sum().sort_values(ascending=False)
if not estado_top.empty:
    texto.append(
        f"- O estado com maior volume total de crimes é **{estado_top.index[0]}**."
    )

if len(evolucao) >= 2:
    ano_inicial = evolucao.index[0]
    ano_final = evolucao.index[-1]
    v_inicial = evolucao.iloc[0]
    v_final = evolucao.iloc[-1]
    if v_final > v_inicial:
        tendencia = "aumento"
    elif v_final < v_inicial:
        tendencia = "queda"
    else:
        tendencia = "estabilidade"
    texto.append(
        f"- Entre **{ano_inicial}** e **{ano_final}**, observa-se um **{tendencia}** "
        f"no total de crimes registrados (de {int(v_inicial):,} para {int(v_final):,}).".replace(",", ".")
    )

for linha in texto:
    st.write(linha)
