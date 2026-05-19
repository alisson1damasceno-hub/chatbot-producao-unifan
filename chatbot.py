import pandas as pd

# ── Carrega as planilhas ──────────────────────────────────────────
intencoes = pd.read_csv("Intencoes.csv")
manutencao = pd.read_csv("manutencao_tecidos.csv")

# ── Estado da conversa ───────────────────────────────────────────
estado = {
    "aguardando_followup": False,
    "intencao_ativa": None
}

# ── Funções ──────────────────────────────────────────────────────
def identificar_intencao(mensagem):
    mensagem = mensagem.lower()
    for _, row in intencoes.iterrows():
        palavras = row["palavras_chave"].split(",")
        for palavra in palavras:
            if palavra.strip() in mensagem:
                return row
    return None

def buscar_subtipo(mensagem, tabela):
    mensagem = mensagem.lower()
    for _, row in tabela.iterrows():
        palavras = row["palavras_chave"].split(",")
        for palavra in palavras:
            if palavra.strip() in mensagem:
                return row["resposta_padrao"]
    return "Não reconheci essa opção. Tente novamente com uma das alternativas sugeridas."

def processar_mensagem(mensagem):
    if estado["aguardando_followup"]:
        intencao_id = estado["intencao_ativa"]

        if intencao_id == "manutencao":
            resposta = buscar_subtipo(mensagem, manutencao)

        estado["aguardando_followup"] = False
        estado["intencao_ativa"] = None
        return resposta

    intencao = identificar_intencao(mensagem)

    if intencao is None:
        return "Desculpe, não entendi. Pode reformular?"

    if intencao["tipo_resposta"] == "guiada":
        estado["aguardando_followup"] = True
        estado["intencao_ativa"] = intencao["id_intencao"]
        return intencao["pergunta_followup"]

    return intencao["resposta_padrao"]

# ── Loop principal ───────────────────────────────────────────────
print("Chatbot iniciado! Digite 'sair' para encerrar.\n")

while True:
    mensagem = input("Você: ")
    if mensagem.lower() == "sair":
        print("Bot: Até logo!")
        break
    resposta = processar_mensagem(mensagem)
    print(f"Bot: {resposta}\n")