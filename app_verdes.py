import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa Firebase apenas uma vez
if not firebase_admin._apps:
    firebase_config = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

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
from urllib.request import urlopen

try:
    logo_url = "https://storage.googleapis.com/ire-74774-ope/files%2Fmigration%2Ftb_releases-5238-604.jpg"
    logo = Image.open(urlopen(logo_url))
    st.sidebar.image(logo, use_container_width=True)
except Exception as e:
    st.sidebar.write("Erro ao carregar a logo:", e)


CSV_FILE = "emprestimos_placa_verde.csv"  # backup local opcional


def carregar_dados():
    # Busca dados do Firestore
    try:
        docs = db.collection("emprestimos_placa_verde").stream()
        registros = [doc.to_dict() for doc in docs]
        if registros:
            df = pd.DataFrame(registros)
            return df
        else:
            # Estrutura base se não houver dados no Firestore
            cols = [
                "Nome Solicitante", "Email Solicitante", "IPN Solicitante", "Departamento",
                "Telefone Solicitante", "Numero cnh", "Validade CNH", "Nome Supervisor",
                "Email Supervisor", "Motivo", "Previsão Devolução", "Declaração Lida",
                "GoodCard", "SV Veículo", "Pernoite", "Projeto", "Data Registro",
                "Placa", "Data Devolução Real"
            ]
            return pd.DataFrame(columns=cols)
    except Exception as e:
        st.error(f"Erro ao carregar dados do Firestore: {e}")
        # fallback CSV local
        if os.path.exists(CSV_FILE):
            return pd.read_csv(CSV_FILE)
        else:
            return pd.DataFrame()


def salvar_dados(df):
    # Apenas backup local
    df.to_csv(CSV_FILE, index=False)


def adicionar_registro(novo_dado):
    # Salva no Firestore
    try:
        db.collection("emprestimos_placa_verde").add(novo_dado)
    except Exception as e:
        st.error(f"Erro ao salvar no Firestore: {e}")

    # Salva no CSV local também (opcional)
    df = carregar_dados()
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    salvar_dados(df)


# ----------------- Menu lateral -----------------
menu_opcao = st.sidebar.selectbox("Navegação", ["Formulário de Solicitação", "Registros de Empréstimos"])

# ----------------- Página: Formulário -----------------
if menu_opcao == "Formulário de Solicitação":
    st.subheader("Regras para Utilização da Placa Verde")

    with st.expander("Clique para ver as regras de utilização da Placa Verde"):
        regras_texto = """
        (Seu texto de regras aqui)
        """
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
            st.markdown("""
            **Em caso de sinistro, seguir os procedimentos abaixo:**
            - Obter dados do terceiro (nome, telefone, endereço, placa, seguradora).  
            - Acionar a **Renault Assistance (0800-0555615)**.  
            - Acompanhar o veículo até a fábrica (Portaria 5).  
            - Providenciar Boletim de Ocorrência.  
            - Comunicar segurança patrimonial, gestão de frota e responsável pela placa verde (CUET DE-TV).
            """)

        declaracao = st.checkbox("Li e estou ciente das informações da Resolução Nº 793/94.")
        confirmacao_info = st.checkbox("Confirmo que as informações fornecidas estão corretas.")

        submit = st.form_submit_button("Enviar Solicitação")

        if submit:
            # Valida campos obrigatórios
            obrigatorios = [nome_solicitante, email_solicitante, departamento, telefone, cnh, motivo, projeto, sv]
            if not all(obrigatorios):
                st.warning("Preencha todos os campos obrigatórios.")
            elif not declaracao:
                st.warning("Você deve confirmar a leitura da declaração.")
            elif not confirmacao_info:
                st.warning("Você deve confirmar que as informações estão corretas.")
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
                    # Campos adicionais para manter consistência
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

        # Garantir colunas essenciais
        if "Placa" not in df.columns:
            df["Placa"] = ""
        if "Data Devolução Real" not in df.columns:
            df["Data Devolução Real"] = ""

        # Converter datas para datetime
        df["Previsão Devolução"] = pd.to_datetime(df["Previsão Devolução"], dayfirst=True, errors='coerce')
        df["Data Devolução Real"] = pd.to_datetime(df["Data Devolução Real"], dayfirst=True, errors='coerce')

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
        with st.container():
            col1, col2, col3 = st.columns([3, 3, 2])
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

        df_exibicao = df.copy()

        colunas_texto = [
            "Nome Solicitante", "Email Solicitante", "Departamento", "IPN Solicitante", "Telefone Solicitante",
            "Numero cnh", "Validade CNH", "Nome Supervisor", "Email Supervisor",
            "Motivo", "GoodCard", "SV Veículo", "Placa", "Pernoite", "Projeto", "Data Registro"
        ]

        for col in colunas_texto:
            if col in df_exibicao.columns:
                df_exibicao[col] = df_exibicao[col].fillna("").astype(str)

        df_exibicao["Previsão Devolução"] = df_exibicao["Previsão Devolução"].dt.strftime("%d/%m/%Y").fillna("")
        df_exibicao["Data Devolução Real"] = df_exibicao["Data Devolução Real"].dt.strftime("%d/%m/%Y").fillna("")

        ordem_colunas = [
            "Status",
            "Previsão Devolução",
            "Data Devolução Real",
            "Nome Solicitante",
            "Email Solicitante",
            "Departamento",
            "IPN Solicitante",
            "Telefone Solicitante",
            "Numero cnh",
            "Validade CNH",
            "Nome Supervisor",
            "Email Supervisor",
            "Motivo",
            "GoodCard",
            "SV Veículo",
            "Placa",
            "Pernoite",
            "Projeto",
            "Data Registro",
        ]

        for col in ordem_colunas:
            if col not in df_exibicao.columns:
                if col == "Status":
                    df_exibicao[col] = df.apply(calcular_status, axis=1)
                else:
                    df_exibicao[col] = ""

        df_exibicao = df_exibicao[ordem_colunas]

        df_editavel = st.data_editor(
            df_exibicao,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_emprestimos",
            disabled=["Status"],
        )

        # Nota: Alterações feitas no data_editor não salvam no Firestore automaticamente.
        # Para atualizar no Firestore, precisa implementar lógica para update, o que pode ser complexo.
        # Por enquanto, mantém somente o CSV local atualizado:
        if not df_editavel.equals(df_exibicao):
            df_editavel["Previsão Devolução"] = pd.to_datetime(df_editavel["Previsão Devolução"], format="%d/%m/%Y", errors='coerce')
            df_editavel["Data Devolução Real"] = pd.to_datetime(df_editavel["Data Devolução Real"], format="%d/%m/%Y", errors='coerce')
            salvar_dados(df_editavel)
            st.success("Alterações salvas no arquivo local CSV.")

