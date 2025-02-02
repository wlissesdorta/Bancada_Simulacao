from machine import Pin, UART
import utime

# Configuração do UART (somente TX utilizado)
uart = UART(1, baudrate=9600, tx=Pin(8))  # Apenas TX configurado

# Configuração manual dos sensores, nomeados diretamente
SA = Pin(15, Pin.IN, Pin.PULL_DOWN)
SB = Pin(7, Pin.IN, Pin.PULL_DOWN)
SC = Pin(6, Pin.IN, Pin.PULL_DOWN)
SD = Pin(5, Pin.IN, Pin.PULL_DOWN)
SE = Pin(4, Pin.IN, Pin.PULL_DOWN)
SF = Pin(3, Pin.IN, Pin.PULL_DOWN)
SG = Pin(2, Pin.IN, Pin.PULL_DOWN)
SH = Pin(0, Pin.IN, Pin.PULL_DOWN)
SI = Pin(14, Pin.IN, Pin.PULL_DOWN)

# Lista ordenada de sensores para priorizar o mais alto
sensores = [
    ("SA", SA),
    ("SB", SB),
    ("SC", SC),
    ("SD", SD),
    ("SE", SE),
    ("SF", SF),
    ("SG", SG),
    ("SH", SH),
    ("SI", SI)
]

while True:
    mensagem_ativa = "NA"  # Mensagem padrão se nenhum sensor estiver ativo

    # Percorre os sensores na ordem inversa para priorizar o mais alto
    for nome, sensor in reversed(sensores):
        if sensor.value():
            mensagem_ativa = nome
            break  # Encontrado o sensor mais alto ativo

    print(f"Enviando: {mensagem_ativa}")
    uart.write(mensagem_ativa + "\n")  # Envia a mensagem correspondente via UART

    utime.sleep(0.1)  # Pequeno atraso para evitar loop excessivo
