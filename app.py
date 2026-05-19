import streamlit as st
import pandas as pd

# ── Carrega as planilhas ──────────────────────────────────────────
intencoes = pd.read_csv("Intencoes.csv")

tabelas_guiadas = {
    "manutencao": pd.read_csv("manutencao_tecidos.csv"),
}

# ── Funções ──────────────────────────────────────────────────────
def identificar_intencoes(mensagem):
    mensagem = mensagem.lower()
    encontradas = []
    for _, row in intencoes.iterrows():
        palavras = row["palavras_chave"].split(",")
        for palavra in palavras:
            if palavra.strip() in mensagem:
                encontradas.append(row)
                break
    return encontradas

def buscar_subtipo(mensagem, tabela):
    mensagem = mensagem.lower()
    for _, row in tabela.iterrows():
        palavras = row["palavras_chave"].split(",")
        for palavra in palavras:
            if palavra.strip() in mensagem:
                return row["resposta_padrao"]
    return None

def processar_mensagem(mensagem):
    if st.session_state.aguardando_followup:
        intencao_id = st.session_state.intencao_ativa
        tabela = tabelas_guiadas.get(intencao_id)
        resposta = buscar_subtipo(mensagem, tabela)

        st.session_state.aguardando_followup = False
        st.session_state.intencao_ativa = None

        if resposta is None:
            return "Não reconheci essa opção. Tente novamente com as alternativas sugeridas."
        return resposta

    intencoes_encontradas = identificar_intencoes(mensagem)

    if not intencoes_encontradas:
        return "Desculpe, não entendi. Pode reformular?"

    respostas = []
    guiada_pendente = None

    for intencao in intencoes_encontradas:
        if intencao["tipo_resposta"] == "direta":
            respostas.append(intencao["resposta_padrao"])
        elif intencao["tipo_resposta"] == "guiada":
            guiada_pendente = intencao

    if guiada_pendente is not None:
        intencao_id = guiada_pendente["id_intencao"]
        tabela = tabelas_guiadas.get(intencao_id)

        resposta_direta = buscar_subtipo(mensagem, tabela)
        if resposta_direta:
            respostas.append(resposta_direta)
        else:
            st.session_state.aguardando_followup = True
            st.session_state.intencao_ativa = intencao_id
            respostas.append(guiada_pendente["pergunta_followup"])

    return "\n".join(respostas)

# ── Interface ─────────────────────────────────────────────────────
st.title("Chatbot - Produção Unifan")

if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "aguardando_followup" not in st.session_state:
    st.session_state.aguardando_followup = False
if "intencao_ativa" not in st.session_state:
    st.session_state.intencao_ativa = None

for msg in st.session_state.mensagens:
    with st.chat_message(msg["papel"]):
        st.write(msg["texto"])

if entrada := st.chat_input("Digite sua mensagem..."):
    st.session_state.mensagens.append({"papel": "user", "texto": entrada})
    with st.chat_message("user"):
        st.write(entrada)

    resposta = processar_mensagem(entrada)

    st.session_state.mensagens.append({"papel": "assistant", "texto": resposta})
    with st.chat_message("assistant"):
        st.write(resposta)