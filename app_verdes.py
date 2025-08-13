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
def adicionar_registro(dado):
    db.collection("emprestimos_placa_verde").add(dado)

def buscar_dados():
    docs = db.collection("emprestimos_placa_verde").stream()
    registros = []
    for doc in docs:
        reg = doc.to_dict()
        reg["Firestore_ID"] = doc.id  # adiciona ID do Firestore
        registros.append(reg)
    return pd.DataFrame(registros)

def atualizar_registro(doc_id, dado_atualizado):
    db.collection("emprestimos_placa_verde").document(doc_id).set(dado_atualizado)

# ----------------- Configurações Iniciais -----------------
st.set_page_config(
    page_title="Controle de Empréstimo de Placa Verde",
    layout="wide"
)

st.markdown("""
    <style>
    .titulo-renault {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        color: #FFD700;
        margin-top: -40px;
    }
    section[data-testid="stSidebar"] {
        background-color: black;
        color: white;
    }
    .css-1cpxqw2, .css-qbe2hs, .css-1v0mbdj, .css-1xarl3l {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo-renault">RENAULT</div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Controle de Empréstimo - Placa Verde</h1>", unsafe_allow_html=True)

# ----------------- Logo Sidebar -----------------
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
        regras_texto = """<SEU TEXTO DE REGRAS AQUI>"""
        st.markdown(regras_texto)

    st.subheader("Formulário de Solicitação de Empréstimo")

    with st.form("form_emprestimo"):
        col1, col2 = st.columns(2)
        with col1:
            nome_solicitante = st.text_input("Nome Completo do Solicitante", placeholder="João da Silva")
            email_solicitante = st.text_input("Email do Solicitante", placeholder="joao.silva@renault.com")
            ipn = st.text_input("IPN do Solicitante", placeholder="PM51532")
            departamento = st.text_input("Departamento", placeholder="DE-TR")
            telefone = st.text_input("Telefone", placeholder="33803030 ou 988774433")
            cnh = st.text_input("Número da CNH")
            validade_cnh = st.date_input("Validade da CNH", format="DD/MM/YYYY")
        with col2:
            nome_supervisor = st.text_input("Nome Completo do Supervisor", placeholder="Mario de Andrade")
            email_supervisor = st.text_input("Email do Supervisor", placeholder="mario.andrade@renault.com")
            sv = st.text_input("SV do Veículo")
            projeto = st.text_input("Projeto", placeholder="Ex: HJD - R1312 - F67")
            goodcard = st.radio("Necessita de cartão GoodCard?", ["NÃO", "SIM"], horizontal=True)
            pernoite = st.radio("Utilização com pernoite?", ["NÃO", "SIM"], horizontal=True)

        motivo = st.text_area("Local e motivo da utilização", placeholder="Circuitos CPVL para ensaio de durabilidade do projeto XXX")
        previsao_devolucao = st.date_input("Previsão de Devolução", format="DD/MM/YYYY")

        with st.expander("Leia as orientações em caso de sinistro"):
            st.markdown("<TEXTO DE ORIENTAÇÃO DE SINISTRO AQUI>")

        declaracao = st.checkbox("Li e estou ciente das informações da Resolução Nº 793/94.")
        confirmacao_info = st.checkbox("Confirmo que as informações fornecidas estão corretas.")

        submit = st.form_submit_button("Enviar Solicitação")

        if submit:
            if not all([nome_solicitante, email_solicitante, ipn, departamento, telefone, cnh, validade_cnh, nome_supervisor, email_supervisor, sv, projeto, goodcard, pernoite, motivo, previsao_devolucao]):
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
                adicionar_registro(dados)
                st.success("Solicitação registrada com sucesso.")

# ----------------- Página: Registros -----------------
elif menu_opcao == "Registros de Empréstimos":
    st.subheader("Área Protegida - Registros de Empréstimos")
    senha_correta = "renault2025"
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        senha_entrada = st.text_input("🔐 Digite a senha para acessar os registros:", type="password")
        if senha_entrada == senha_correta:
            st.session_state["autenticado"] = True
            st.success("Acesso autorizado com sucesso.")
        elif senha_entrada:
            st.error("Senha incorreta. Tente novamente.")
        else:
            st.info("Digite a senha para visualizar os registros.")

    if st.session_state["autenticado"]:
        df = buscar_dados()

        # Adiciona colunas se não existirem
        for col in ["Placa", "Data Devolução Real"]:
            if col not in df.columns:
                df[col] = ""

        # Converte datas
        for col in ["Previsão Devolução", "Data Devolução Real"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

        # Status
        def calcular_status(row):
            hoje = datetime.now().date()
            if pd.notnull(row.get("Data Devolução Real")):
                return "Devolvido"
            elif pd.notnull(row.get("Previsão Devolução")) and hoje > row["Previsão Devolução"].date():
                return "Atrasado"
            else:
                return "Em aberto"

        df["Status"] = df.apply(calcular_status, axis=1)

        # Filtros
        col1, col2, col3 = st.columns([3,3,2])
        with col1:
            nome_filtro = st.text_input("Filtrar por Nome do Solicitante")
        with col2:
            sv_filtro = st.text_input("Filtrar por SV do Veículo")
        with col3:
            status_opcoes = df["Status"].unique().tolist() if not df.empty else []
            status_filtro = st.multiselect("Filtrar por Status", options=status_opcoes, default=status_opcoes)

        if nome_filtro:
            df = df[df["Nome Supervisor"].astype(str).str.contains(nome_filtro, case=False, na=False)]
        if sv_filtro:
            df = df[df["SV Veículo"].astype(str).str.contains(sv_filtro, case=False, na=False)]
        if status_filtro:
            df = df[df["Status"].isin(status_filtro)]

        # Prepara para edição
        df_exibicao = df.copy()
        colunas_texto = [
            "Nome Solicitante", "Email Solicitante", "Departamento", "IPN Solicitante",
            "Telefone", "Numero CNH", "Validade CNH", "Nome Supervisor", "Email Supervisor",
            "Motivo", "GoodCard", "SV Veículo", "Placa", "Pernoite", "Projeto", "Data Registro"
        ]
        for col in colunas_texto:
            if col in df_exibicao.columns:
                df_exibicao[col] = df_exibicao[col].fillna("").astype(str)

        for col in ["Previsão Devolução", "Data Devolução Real"]:
            if col in df_exibicao.columns:
                df_exibicao[col] = df_exibicao[col].dt.strftime("%d/%m/%Y").fillna("")

        ordem_colunas = [
            "Status","Previsão Devolução","Data Devolução Real","Nome Solicitante","Email Solicitante",
            "Departamento","IPN Solicitante","Telefone","Numero CNH","Validade CNH","Nome Supervisor",
            "Email Supervisor","Motivo","GoodCard","SV Veículo","Placa","Pernoite","Projeto","Data Registro"
        ]
        for col in ordem_colunas:
            if col not in df_exibicao.columns:
                df_exibicao[col] = ""

        df_exibicao = df_exibicao[ordem_colunas]

        df_editavel = st.data_editor(
            df_exibicao,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_emprestimos",
            disabled=["Status"],
        )

        # Atualiza Firestore se houver mudanças
        if not df_editavel.equals(df_exibicao):
            for i, row in df_editavel.iterrows():
                doc_id = df.loc[i, "Firestore_ID"]
                atualizar_registro(doc_id, row.to_dict())
            st.success("Registros atualizados no Firestore.")

