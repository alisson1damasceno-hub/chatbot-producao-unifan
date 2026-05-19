import pandas as pd

# ── Carrega a tabela mãe ─────────────────────────────────────────
intencoes = pd.read_csv("Intencoes.csv")

# ── Registra as tabelas filhas aqui ─────────────────────────────
# Para adicionar nova intenção guiada: só adicionar uma linha aqui
tabelas_guiadas = {
    "manutencao": pd.read_csv("manutencao_tecidos.csv"),
}

# ── Estado da conversa ───────────────────────────────────────────
estado = {
    "aguardando_followup": False,
    "intencao_ativa": None
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
    if estado["aguardando_followup"]:
        intencao_id = estado["intencao_ativa"]
        tabela = tabelas_guiadas.get(intencao_id)
        resposta = buscar_subtipo(mensagem, tabela)

        estado["aguardando_followup"] = False
        estado["intencao_ativa"] = None

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
            estado["aguardando_followup"] = True
            estado["intencao_ativa"] = intencao_id
            respostas.append(guiada_pendente["pergunta_followup"])

    return "\n".join(respostas)

# ── Loop principal ───────────────────────────────────────────────
print("Chatbot iniciado! Digite 'sair' para encerrar.\n")

while True:
    mensagem = input("Você: ")
    if mensagem.lower() == "sair":
        print("Bot: Até logo!")
        break
    resposta = processar_mensagem(mensagem)
    print(f"Bot: {resposta}\n")
    