import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
from urllib.request import urlopen
import firebase_admin
from firebase_admin import credentials, firestore

# ----------------- Configurações Iniciais -----------------
st.set_page_config(
    page_title="Controle de Empréstimo de Placa Verde",
    layout="wide"
)

# CSS para sidebar preta e título personalizado
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

# ----------------- Logo na Sidebar -----------------
try:
    logo_url = "https://storage.googleapis.com/ire-74774-ope/files%2Fmigration%2Ftb_releases-5238-604.jpg"
    logo = Image.open(urlopen(logo_url))
    st.sidebar.image(logo, use_container_width=True)
except Exception as e:
    st.sidebar.write("Erro ao carregar a logo:", e)

# ----------------- Configuração do Firestore -----------------
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["FIREBASE"])
    firebase_admin.initialize_app(cred)
db = firestore.client()
COLECAO = "emprestimos_placa_verde"

# ----------------- Funções Firestore -----------------
def carregar_dados():
    docs = db.collection(COLECAO).stream()
    lista = []
    for doc in docs:
        dados = doc.to_dict()
        dados["id_doc"] = doc.id
        lista.append(dados)
    if lista:
        return pd.DataFrame(lista)
    else:
        return pd.DataFrame(columns=[
            "Nome Solicitante", "Email Solicitante", "IPN Solicitante", "Departamento",
            "Telefone Solicitante", "Numero cnh", "Validade CNH", "Nome Supervisor",
            "Email Supervisor", "Motivo", "Previsão Devolução", "Declaração Lida",
            "GoodCard", "SV Veículo", "Pernoite", "Projeto", "Data Registro",
            "Placa", "Data Devolução Real"
        ])

def adicionar_registro(novo_dado):
    db.collection(COLECAO).add(novo_dado)

def atualizar_registro(id_doc, dados_atualizados):
    db.collection(COLECAO).document(id_doc).set(dados_atualizados)

# ----------------- Menu lateral -----------------
menu_opcao = st.sidebar.selectbox("Navegação", ["Formulário de Solicitação", "Registros de Empréstimos"])

# ----------------- Página: Formulário -----------------
if menu_opcao == "Formulário de Solicitação":
    st.subheader("Regras para Utilização da Placa Verde")
    with st.expander("Clique para ver as regras de utilização da Placa Verde"):
        regras_texto = """
**SITUAÇÃO GEOGRÁFICA:**  
O Art. 2º da Resolução 793/94 deixa claro que a utilização da placa verde de "FABRICANTE", independerá de horário, situação geográfica ou restrições de qualquer natureza, respeitado o disposto no Art. 4º e seus parágrafos.

**CONDUTORES/OCUPANTES:**  
O Art. 4º da Resolução 793/94 define que somente podem dirigir ou estar dentro de um veículo com placa verde (mesmo que carona), os colaboradores que estiverem devidamente registrados no DETRAN.

> O processo de registro da documentação (dados e cópia da CNH) dos condutores deve passar pela DE-TV e Frota.  
> É obrigatório o preenchimento do livro preto que acompanha a placa verde antes da saída da fábrica e no retorno.

**INFORMAÇÕES COMPLEMENTARES**  
> A placa está sob responsabilidade do condutor principal identificado abaixo.  
> O documento de licenciamento anual da placa está fixado dentro do livro.  
> Em caso de perda da placa verde, providenciar imediatamente o Boletim de Ocorrência e avisar à segurança patrimonial, gestão de frota e DE-TV.  
> O prazo máximo de empréstimo é de 4 meses para ensaios de Durabilidade e Pré-OLV/OLO, e 2 meses para os demais clientes.

Responsável pelas placas verdes DE-TV -> CUET Fabio Marques
"""
        st.markdown(regras_texto)
    
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
        previsao_devolucao = st.date_input("Previsão de Devolução")

        declaracao = st.checkbox("Li e estou ciente das informações da Resolução Nº 793/94.")
        confirmacao_info = st.checkbox("Confirmo que as informações fornecidas estão corretas.")

        submit = st.form_submit_button("Enviar Solicitação")

        if submit:
            if not all([nome_solicitante, email_solicitante, ipn, departamento, telefone, cnh, validade_cnh,
                        nome_supervisor, email_supervisor, sv, projeto, goodcard, pernoite, motivo, previsao_devolucao]):
                st.warning("Preencha todos os campos obrigatórios.")
            elif not declaracao or not confirmacao_info:
                st.warning("Você deve confirmar todas as declarações.")
            else:
                dados = {
                    "Nome Solicitante": nome_solicitante,
                    "Email Solicitante": email_solicitante,
                    "IPN Solicitante": ipn,
                    "Departamento": departamento,
                    "Telefone Solicitante": telefone,
                    "Numero cnh": cnh, 
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
                    "Data Registro": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Placa": "",
                    "Data Devolução Real": ""
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
        df = carregar_dados()

        # Adiciona colunas se não existirem
        for col in ["Placa", "Data Devolução Real"]:
            if col not in df.columns:
                df[col] = ""

        # Converte datas
        for col in ["Previsão Devolução", "Data Devolução Real"]:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

        # Define status
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
        with col1:
            nome_filtro = st.text_input("Filtrar por Nome do Solicitante")
        with col2:
            sv_filtro = st.text_input("Filtrar por SV do Veículo")
        with col3:
            status_opcoes = df["Status"].unique().tolist()
            status_filtro = st.multiselect("Filtrar por Status", options=status_opcoes, default=status_opcoes)

        if nome_filtro:
            df = df[df["Nome Supervisor"].astype(str).str.contains(nome_filtro, case=False, na=False)]
        if sv_filtro:
            df = df[df["SV Veículo"].fillna("").astype(str).str.contains(sv_filtro, case=False, na=False)]
        if status_filtro:
            df = df[df["Status"].isin(status_filtro)]

        # Prepara DataFrame para exibição/editável
        df_exibicao = df.copy()
        colunas_texto = [
            "Nome Solicitante", "Email Solicitante", "Departamento", "IPN Solicitante", "Telefone Solicitante",
            "Numero cnh", "Validade CNH", "Nome Supervisor", "Email Supervisor",
            "Motivo", "GoodCard", "SV Veículo", "Placa", "Pernoite", "Projeto", "Data Registro"
        ]
        for col in colunas_texto:
            if col in df_exibicao.columns:
                df_exibicao[col] = df_exibicao[col].fillna("").astype(str)
        for col in ["Previsão Devolução", "Data Devolução Real"]:
            df_exibicao[col] = df_exibicao[col].dt.strftime("%d/%m/%Y").fillna("")

        ordem_colunas = [
            "Status", "Previsão Devolução", "Data Devolução Real", "Nome Solicitante",
            "Email Solicitante", "Departamento", "IPN Solicitante", "Telefone Solicitante",
            "Numero cnh", "Validade CNH", "Nome Supervisor", "Email Supervisor", "Motivo",
            "GoodCard", "SV Veículo", "Placa", "Pernoite", "Projeto", "Data Registro", "id_doc"
        ]
        for col in ordem_colunas:
            if col not in df_exibicao.columns:
                df_exibicao[col] = "" if col != "Status" else df.apply(calcular_status, axis=1)
        df_exibicao = df_exibicao[ordem_colunas]

        df_editavel = st.data_editor(
            df_exibicao,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_emprestimos",
            disabled=["Status"]
        )

        # Salva alterações no Firestore
        if not df_editavel.equals(df_exibicao):
            for i, row in df_editavel.iterrows():
                id_doc = row.get("id_doc")
                if id_doc:
                    atualizar_registro(id_doc, row.drop(labels=["id_doc"]).to_dict())
