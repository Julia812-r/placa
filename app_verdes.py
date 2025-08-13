import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
from urllib.request import urlopen
import firebase_admin
from firebase_admin import credentials, firestore

# ----------------- Inicialização Firebase -----------------
firebase_cred = st.secrets["firebase"]  # Ajuste conforme seu Secret
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_cred)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ----------------- Funções Firestore -----------------
def adicionar_registro(colecao, dados):
    doc_ref = db.collection(colecao).add(dados)
    return doc_ref

def buscar_registros(colecao):
    docs = db.collection(colecao).stream()
    registros = []
    for doc in docs:
        r = doc.to_dict()
        r["Firestore_ID"] = doc.id
        registros.append(r)
    return pd.DataFrame(registros)

def atualizar_registro(doc_id, dados):
    db.collection("emprestimos").document(doc_id).update(dados)

# ----------------- Configurações Iniciais -----------------
st.set_page_config(
    page_title="Controle de Empréstimo de Placa Verde",
    layout="wide"
)

st.markdown("""
    <style>
    .titulo-renault { text-align: center; font-size: 42px; font-weight: bold; color: #FFD700; margin-top: -40px; }
    section[data-testid="stSidebar"] { background-color: black; color: white; }
    .css-1cpxqw2, .css-qbe2hs, .css-1v0mbdj, .css-1xarl3l { color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-renault">RENAULT</div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Controle de Empréstimo - Placa Verde</h1>", unsafe_allow_html=True)

# ----------------- Logo -----------------
try:
    logo_url = "https://storage.googleapis.com/ire-74774-ope/files%2Fmigration%2Ftb_releases-5238-604.jpg"
    logo = Image.open(urlopen(logo_url))
    st.sidebar.image(logo, use_container_width=True)
except Exception as e:
    st.sidebar.write("Erro ao carregar a logo:", e)

# ----------------- Menu lateral -----------------
menu_opcao = st.sidebar.selectbox("Navegação", ["Formulário de Solicitação", "Registros de Empréstimos"])

# ----------------- Página: Formulário -----------------
if menu_opcao == "Formulário de Solicitação":
    st.subheader("Regras para Utilização da Placa Verde")

    with st.expander("Clique para ver as regras de utilização da Placa Verde"):
        st.markdown(""" 
        **Regras resumidas e instruções importantes do uso da placa verde.**
        (Copie aqui o texto completo que você já tinha.)
        """)

    st.subheader("Formulário de Solicitação de Empréstimo")
    with st.form("form_emprestimo"):
        col1, col2 = st.columns(2)
        with col1:
            nome_solicitante = st.text_input("Nome Completo do Solicitante")
            email_solicitante = st.text_input("Email do Solicitante")
            ipn = st.text_input("IPN do Solicitante")
            departamento = st.text_input("Departamento")
            telefone = st.text_input("Telefone")
            cnh = st.text_input("Número da CNH")
            validade_cnh = st.date_input("Validade da CNH")
        with col2:
            nome_supervisor = st.text_input("Nome Completo do Supervisor")
            email_supervisor = st.text_input("Email do Supervisor")
            sv = st.text_input("SV do Veículo")
            projeto = st.text_input("Projeto")
            goodcard = st.radio("Necessita de cartão GoodCard?", ["NÃO", "SIM"], horizontal=True)
            pernoite = st.radio("Utilização com pernoite?", ["NÃO", "SIM"], horizontal=True)

        motivo = st.text_area("Local e motivo da utilização")
        previsao_devolucao = st.date_input("Previsão Devolução")

        declaracao = st.checkbox("Li e estou ciente das informações da Resolução Nº 793/94.")
        confirmacao_info = st.checkbox("Confirmo que as informações fornecidas estão corretas.")

        submit = st.form_submit_button("Enviar Solicitação")
        if submit:
            if not all([nome_solicitante, email_solicitante, ipn, departamento, telefone, cnh, validade_cnh,
                        nome_supervisor, email_supervisor, sv, projeto, goodcard, pernoite, motivo, previsao_devolucao]):
                st.warning("Preencha todos os campos obrigatórios.")
            elif not declaracao:
                st.warning("Você deve confirmar a leitura da declaração.")
            else:
                dados = {
                    "Nome Solicitante": nome_solicitante,
                    "Email Solicitante": email_solicitante,
                    "IPN Solicitante": ipn,
                    "Departamento": departamento,
                    "Telefone Solicitante": telefone,
                    "Numero CNH": cnh,
                    "Validade CNH": validade_cnh.strftime("%d/%m/%Y"),
                    "Nome Supervisor": nome_supervisor,
                    "Email Supervisor": email_supervisor,
                    "Motivo": motivo,
                    "Previsão Devolução": previsao_devolucao.strftime("%d/%m/%Y"),
                    "Declaração Lida": "SIM",
                    "GoodCard": goodcard,
                    "SV Veículo": sv,
                    "Pernoite": pernoite,
                    "Projeto": projeto,
                    "Data Registro": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                adicionar_registro("emprestimos", dados)
                st.success("Solicitação registrada com sucesso.")

# ----------------- Página: Registros -----------------
elif menu_opcao == "Registros de Empréstimos":
    st.subheader("Área Protegida - Registros de Empréstimos")
    senha_correta = "renault2025"

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        senha_entrada = st.text_input("🔐 Digite a senha:", type="password")
        if senha_entrada == senha_correta:
            st.session_state["autenticado"] = True
            st.success("Acesso autorizado com sucesso.")
        elif senha_entrada:
            st.error("Senha incorreta. Tente novamente.")

    if st.session_state["autenticado"]:
        df = buscar_registros("emprestimos")

        if "Placa" not in df.columns:
            df["Placa"] = ""
        if "Data Devolução Real" not in df.columns:
            df["Data Devolução Real"] = ""

        # Converte datas para datetime
        df["Previsão Devolução"] = pd.to_datetime(df["Previsão Devolução"], dayfirst=True, errors='coerce')
        df["Data Devolução Real"] = pd.to_datetime(df["Data Devolução Real"], dayfirst=True, errors='coerce')

        # Calcula status
        def calcular_status(row):
            hoje = datetime.now().date()
            if pd.notnull(row["Data Devolução Real"]):
                return "Devolvido"
            elif pd.notnull(row["Previsão Devolução"]) and hoje > row["Previsão Devolução"].date():
                return "Atrasado"
            else:
                return "Em aberto"

        df["Status"] = df.apply(calcular_status, axis=1)

        # Filtros
        col1, col2, col3 = st.columns([3,3,2])
        with col1: nome_filtro = st.text_input("Filtrar por Nome do Solicitante")
        with col2: sv_filtro = st.text_input("Filtrar por SV do Veículo")
        with col3: 
            status_opcoes = df["Status"].unique().tolist()
            status_filtro = st.multiselect("Filtrar por Status", options=status_opcoes, default=status_opcoes)

        if nome_filtro:
            df = df[df["Nome Supervisor"].astype(str).str.contains(nome_filtro, case=False, na=False)]
        if sv_filtro:
            df = df[df["SV Veículo"].astype(str).str.contains(sv_filtro, case=False, na=False)]
        if status_filtro:
            df = df[df["Status"].isin(status_filtro)]

        # Data Editor
        df_editavel = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_emprestimos",
            disabled=["Status"]
        )

        # Atualiza Firestore
        for i, row in df_editavel.iterrows():
            if "Firestore_ID" in row:
                atualizar_registro(row["Firestore_ID"], row.to_dict())
        st.success("Registros sincronizados com Firestore.")
