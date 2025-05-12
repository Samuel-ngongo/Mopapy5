import random
import statistics

historico = []
max_historico = 100

def adicionar_valor(valor):
    if len(historico) >= max_historico:
        historico.pop(0)
    historico.append(valor)

def media_valores():
    if len(historico) < 2:
        return 0
    return round(statistics.mean(historico), 2)

def desvio_padrao():
    if len(historico) < 2:
        return 0
    return round(statistics.stdev(historico), 2)

def probabilidade_proximo_valor():
    if len(historico) < 10:
        return "Dados insuficientes"
    
    ultimos = historico[-10:]
    altos = sum(1 for x in ultimos if x >= 2)
    baixos = 10 - altos

    prob_alto = round((altos / 10) * 100, 2)
    prob_baixo = round((baixos / 10) * 100, 2)

    return {
        "Chance de Alto (>=2x)": f"{prob_alto}%",
        "Chance de Baixo (<2x)": f"{prob_baixo}%"
    }

def detectar_mudanca_padrao():
    if len(historico) < 20:
        return "Aguardando mais dados..."
    
    bloco1 = historico[-20:-10]
    bloco2 = historico[-10:]

    media1 = statistics.mean(bloco1)
    media2 = statistics.mean(bloco2)

    diferenca = abs(media1 - media2)

    if diferenca > 1.5:
        return "Possível mudança brusca de padrão detectada!"
    return "Padrão estável"

def proxima_previsao():
    if len(historico) < 3:
        return "Aguardando dados..."

    ultimos = historico[-3:]

    if all(x >= 2 for x in ultimos):
        return "Alerta: Após vários altos, pode vir queda"
    elif all(x < 1.5 for x in ultimos):
        return "Após vários baixos, chance de valor alto"
    else:
        return "Tendência mista detectada"

# Exemplo de simulação
for _ in range(50):
    valor = round(random.uniform(0.5, 3.5), 2)
    adicionar_valor(valor)

print("Histórico:", historico)
print("Média:", media_valores())
print("Desvio padrão:", desvio_padrao())
print("Probabilidade:", probabilidade_proximo_valor())
print("Mudança de padrão:", detectar_mudanca_padrao())
print("Previsão próxima rodada:", proxima_previsao())
