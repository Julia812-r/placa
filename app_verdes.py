import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

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

# Título principal
st.markdown('<div class="titulo-renault">RENAULT</div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center;'>Controle de Empréstimo - Placa Verde</h1>", unsafe_allow_html=True)

# ----------------- Logo na Sidebar -----------------
from PIL import Image
from urllib.request import urlopen

try:
    logo_url = "https://storage.googleapis.com/ire-74774-ope/files%2Fmigration%2Ftb_releases-5238-604.jpg"
    logo = Image.open(urlopen(logo_url))
    st.sidebar.image(logo, use_container_width=True)
except Exception as e:
    st.sidebar.write("Erro ao carregar a logo:", e)


# ----------------- Funções Auxiliares -----------------
CSV_FILE = "emprestimos_placa_verde.csv"

def carregar_dados():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=[
            "Nome Supervisor", "Email", "Departamento", "Telefone", "CNH", "Validade CNH",
            "Motivo", "Previsão Devolução", "Declaração Lida",
            "GoodCard", "SV Veículo", "Pernoite", "Projeto", "Data Registro"
        ])

def salvar_dados(df):
    df.to_csv(CSV_FILE, index=False)

def adicionar_registro(novo_dado):
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
**SITUAÇÃO GEOGRÁFICA:**  
O Art. 2º da Resolução 793/94 deixa claro que a utilização da placa verde de "FABRICANTE", independerá de horário, situação geográfica ou restrições de qualquer natureza, respeitado o disposto no Art. 4º e seus parágrafos.

**CONDUTORES/OCUPANTES:**  
O Art. 4º da Resolução 793/94 define que somente podem dirigir ou estar dentro de um veículo com placa verde (mesmo que carona), os colaboradores que estiverem devidamente registrados no DETRAN. Verificar que Técnicos Especializados de empresas prestadoras de serviço também podem conduzir os veículos, desde que atendam ao requisito de registro no DETRAN. É indispensável o correto preenchimento e manutenção constante do registro de utilização das placas verdes (livro preto).

> O processo de registro da documentação (dados e cópia da CNH) dos condutores deve passar pela DE-TV e Frota.  
> É obrigatório o preenchimento do livro preto que acompanha a placa verde antes da saída da fábrica e no retorno.  
> O veículo de ensaio é de propriedade da Empresa Renault do Brasil.  
> Todo uso particular é rigorosamente proibido.  
> A hierarquia do condutor deverá estar ciente que o mesmo está utilizando o veículo.

**INFORMAÇÕES COMPLEMENTARES**  
> A placa está sob responsabilidade do condutor principal identificado abaixo.  
> O documento de licenciamento anual da placa está fixado dentro do livro.  
> Em caso de perda da placa verde, providenciar imediatamente o Boletim de Ocorrência e avisar à segurança patrimonial, gestão de frota e DE-TV.  
> Em caso de multa no período de empréstimo da placa, o condutor registrado no livro preto durante a saída do veículo será responsável pelo pagamento e pela pontuação.  
> O condutor deverá portar crachá da Renault, CNH (carteira de motorista) válida e carteirinha de placa verde.  
( * ) O período de responsabilidade corresponde a retirada da placa verde até a respectiva devolução.  
( * ) Devolver a placa verde, livro preto e pasta plástica A0 diretamente ao chefe do atelier DE-TV para cadastro completo da devolução.  
> O prazo máximo de empréstimo de placa verde é de 4 meses para ensaios de Durabilidade e Pré-OLV/OLO, e 2 meses para os demais clientes. Se necessário a prolongação do empréstimo, o cliente deve devolver a placa atual dentro do prazo estipulado e então fazer uma nova demanda.

/!\\ Em caso de descumprimento das regras e resoluções o colaborador que realizou o empréstimo da placa verde fica totalmente responsável por eventuais consequências de processos ou custos associados.

Responsável pelas placas verdes DE-TV -> CUET Fabio Marques
"""

        st.markdown(regras_texto)
    
    st.subheader("Formulário de Solicitação de Empréstimo")
    
    # ... segue o seu formulário aqui ...


    with st.form("form_emprestimo"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo do Supervisor", placeholder="Mario de Andrade")
            email = st.text_input("Email", placeholder="mario.andrade@renault.com")
            telefone = st.text_input("Telefone", placeholder="33803030 ou 988774433")
            cnh = st.text_input("Número da CNH")
            validade_cnh = st.date_input("Validade da CNH", format="DD/MM/YYYY")
        with col2:
            departamento = st.text_input("Departamento", placeholder="DE-TR")
            sv = st.text_input("SV do Veículo")

        # ✅ CAMPO NOVO: Número da Placa com sugestões
        placas_cadastradas = [
            "APE-8033", "APE-1881", "APE-7948", "APE-8020", "APE-7953", "APE-0I26",
            "APE-0817", "APE-8032", "APE-0668", "APE-1423", "APE-8025", "APE-0766",
            "APE-1817", "APE-0739", "APE-8026", "APE-1425", "APE-7960", "APE-7961",
            "APE-8030", "APE-0825", "APE-0782", "APE-0736", "APE-7950", "APE-7710",
            "APE-0737", "APE-8029", "APE-7956", "APE-0786", "APE-1426", "APE-0821",
            "APE-8027", "APE-7954", "APE-0H38", "APE-1427", "APE-7955", "APE-7949",
            "APE-8028", "APE-0823", "APE-0815", "APE-7951", "APE-0768", "APE-1461",
            "APE-7957", "APE-7959", "APE-0806", "APE-0667", "APE-7947", "APE-0812",
            "APE-0824"
        ]

        placa_digitada = st.text_input("Número da Placa", placeholder="Ex: APE-0812")

        sugestoes = [p for p in placas_cadastradas if placa_digitada.upper() in p]
        if placa_digitada and sugestoes:
            st.markdown("**Sugestões encontradas:**")
            for s in sugestoes:
                st.markdown(f"- {s}")

        projeto = st.text_input("Projeto", placeholder="Ex: HJD - R1312 - F67")
        goodcard = st.radio("Necessita de cartão GoodCard?", ["NÃO", "SIM"], horizontal=True)
        pernoite = st.radio("Utilização com pernoite?", ["NÃO", "SIM"], horizontal=True)


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

        # Novo checkbox adicional
        confirmacao_info = st.checkbox("Confirmo que as informações fornecidas estão corretas.")

        submit = st.form_submit_button("Enviar Solicitação")

        if submit:
            if not all([nome, email, departamento, telefone, cnh, motivo, projeto, sv]):
                st.warning("Preencha todos os campos obrigatórios.")
            elif not declaracao:
                st.warning("Você deve confirmar a leitura da declaração.")
            else:
                dados = {
                    "Nome Supervisor": nome,
                    "Email": email,
                    "Departamento": departamento,
                    "Telefone": telefone,
                    "CNH": cnh,
                    "Validade CNH": validade_cnh.strftime("%d/%m/%Y"),
                    "Motivo": motivo,
                    "Previsão Devolução": previsao_devolucao.strftime("%d/%m/%Y"),
                    "Declaração Lida": "SIM",
                    "GoodCard": goodcard,
                    "SV Veículo": sv,
                    "Placa": placa_digitada.upper(),
                    "Pernoite": pernoite,
                    "Projeto": projeto,
                    "Data Registro": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                adicionar_registro(dados)
                st.success("Solicitação registrada com sucesso.")

# ----------------- Página: Registros -----------------
elif menu_opcao == "Registros de Empréstimos":
    st.subheader("Área Protegida - Registros de Empréstimos")

    # Define a senha correta
    senha_correta = "renault2025"

    # Inicializa o estado de autenticação
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    # Se ainda não autenticado, pede a senha
    if not st.session_state["autenticado"]:
        senha_entrada = st.text_input("🔐 Digite a senha para acessar os registros:", type="password")
        if senha_entrada == senha_correta:
            st.session_state["autenticado"] = True
            st.success("Acesso autorizado com sucesso.")
        elif senha_entrada:
            st.error("Senha incorreta. Tente novamente.")
        else:
            st.info("Digite a senha para visualizar os registros.")

    # Se autenticado, exibe os dados
    if st.session_state["autenticado"]:
        df = carregar_dados()

        # Adiciona colunas se não existirem
        if "Placa" not in df.columns:
            df["Placa"] = ""
        if "Data Devolução Real" not in df.columns:
            df["Data Devolução Real"] = ""

        # Converte datas
        df["Previsão Devolução"] = pd.to_datetime(df["Previsão Devolução"], dayfirst=True, errors='coerce')
        df["Data Devolução Real"] = pd.to_datetime(df["Data Devolução Real"], dayfirst=True, errors='coerce')

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
        with st.container():
            col1, col2, col3 = st.columns([3, 3, 2])
            with col1:
                nome_filtro = st.text_input("Filtrar por Nome do Supervisor")
            with col2:
                sv_filtro = st.text_input("Filtrar por SV do Veículo")
            with col3:
                status_opcoes = df["Status"].unique().tolist()
                status_filtro = st.multiselect("Filtrar por Status", options=status_opcoes, default=status_opcoes)

        # Aplica filtros
        if nome_filtro:
            df = df[df["Nome Supervisor"].astype(str).str.contains(nome_filtro, case=False, na=False)]
        if sv_filtro:
            df = df[df["SV Veículo"].fillna("").astype(str).str.contains(sv_filtro, case=False, na=False)]
        if status_filtro:
            df = df[df["Status"].isin(status_filtro)]

        # Mostra tabela com campos editáveis
        st.markdown("### Tabela de Empréstimos")
        df_exibicao = df.copy()

        ordem_colunas = [
            "Status",
            "Previsão Devolução",
            "Data Devolução Real",
            "Nome Supervisor",
            "Email",
            "Departamento",
            "Telefone",
            "CNH",
            "Validade CNH",
            "Motivo",
            "Declaração Lida",
            "GoodCard",
            "SV Veículo",
            "Placa",
            "Pernoite",
            "Projeto",
            "Data Registro",
        ]

        df_exibicao = df_exibicao[ordem_colunas]

        df_editavel = st.data_editor(
            df_exibicao,
            num_rows="dynamic",
            use_container_width=True,
            key="editor_emprestimos",
            disabled=["Status"],
        )

        # Verifica alterações
        if not df_editavel.equals(df):
            salvar_dados(df_editavel)
            
