# ======================================================================
#  INICIO - Importações 
# ======================================================================
#region


from machine import SPI, Pin, ADC, PWM, UART
import ili9341
from ili9341 import Display 
import utime, time
from xglcd_font import XglcdFont



# ======================================================================
#  FIM - Importações 
# ======================================================================
#endregion


# ======================================================================
#  INICIO - # Pinos Utilizados
# ======================================================================
#region

# --------------------------------------------
# | Nome         | GPIO | Descrição           |
# |--------------|------|---------------------|
# | TFT_MISO_PIN | 4    | MISO da tela        |
# | PinoRotametro| 5    | UART Rotâmetro      |
# | TFT_CLK_PIN  | 6    | Clock da tela       |
# | TFT_MOSI_PIN | 7    | MOSI da tela        |
# | bt_baixo     | 8    | Botão Baixo         |
# | bt_esquerda  | 9    | Botão Esquerda      |
# | bt_direita   | 10   | Botão Direita       |
# | bt_cima      | 11   | Botão Cima          |
# | bt_ok        | 12   | Botão OK            |
# | TFT_CS_PIN   | 13   | Chip select da tela |
# | TFT_RST_PIN  | 14   | Reset da tela       |
# | TFT_DC_PIN   | 15   | Data control da tela|
# | bt_acionar   | 18   | Botão acionar       |
# | bt_voltar    | 3   | Botão voltar         |
# | pwm_pin      | 20   | PWM                 |
# | Potenciometro| 26   | ADC Potenciômetro   |
# | sensor_rpm   | 27   | Sensor de RPM       |
# | servo        | 22   | PWM Servo           |
# | Sensor_Mec   | 21   | Sensor Mecanico     | 
# | Lampada      | 19   | Lampada             |
# --------------------------------------------


# Pinos
bt_ok = 12       # Pino do botão OK
bt_cima = 8     # Pino do botão Cima
bt_baixo = 11     # Pino do botão Baixo
bt_direita = 9  # Pino do botão Direita
bt_esquerda = 10  # Pino do botão Esquerda
bt_acionar = 18  # Pino do botão acionar
bt_voltar = 3    # Pino do botão voltar
potenciometro = 26 # Pino do potenciômetro
pino_pwm = 20  # Pino do PWM do inversor
servo = 22     # Pino do servo do rotâmetro
pino_rotametro = 5 # Pino UART Rotametro
sensor_mec = 21 # Pino Sensor Mecanico
lampada = 19    # Pino da lâmpada
sensor_rpm = 27 # Pino do sensor de RPM



# Inicializa os pinos dos botões direcionais como entrada com pull-up
BT_Ok = Pin(bt_ok, Pin.IN, Pin.PULL_UP)
BT_Cima = Pin(bt_cima, Pin.IN, Pin.PULL_UP)
BT_Direita = Pin(bt_direita, Pin.IN, Pin.PULL_UP)
BT_Esquerda = Pin(bt_esquerda, Pin.IN, Pin.PULL_UP)
BT_Baixo = Pin(bt_baixo, Pin.IN, Pin.PULL_UP)
BT_Voltar = Pin(bt_voltar, Pin.IN, Pin.PULL_UP)
Bt_Acionar = Pin(bt_acionar, Pin.IN, Pin.PULL_UP)


# ======================================================================
#  FIM - # Pinos Utilizados
# ======================================================================
#endregion


# ======================================================================
#  INICIO - Configuração de sensor e atuadores
# ======================================================================
#region

# Sensor Mecanico
Sensor_Mecanico = Pin(sensor_mec, Pin.IN, Pin.PULL_UP)

# Sensor de RPM
Sensor_RPM = Pin(sensor_rpm, Pin.IN, Pin.PULL_UP)

# Lampada
Lampada = Pin(lampada, Pin.OUT, Pin.PULL_DOWN)

# Potenciômetro do Painel
Potenciometro = ADC(Pin(potenciometro))

# PWM do inversor
PWM_Inversor = PWM(Pin(pino_pwm))
PWM_Inversor.freq(1000)  # Frequência do PWM

#Servo do rotâmetro
Servo = PWM(Pin(servo))  # Saída PWM
Servo.freq(50)        # Frequência para controle de servo (50 Hz)


#Inicia desligado
Servo.duty_ns(1516667)
PWM_Inversor.duty_u16(0)
Lampada.value(0)


# ======================================================================
#  FIM - Configuração de sensor e atuadores
# ======================================================================
#endregion


# ======================================================================
#  INICIO - Configuração da Tela ili9341
# ======================================================================
#region 

# Configura Tela ili9341
'VCC' 
'GND'
TFT_CS_PIN = const(13)  # Define o pino de chip select para a tela
TFT_RST_PIN = const(14)  # Define o pino de reset para a tela
TFT_DC_PIN = const(15)  # Define o pino de data control (comando/dados) para a tela
TFT_MOSI_PIN = const(7)  # Define o pino de saída de dados (MOSI) para a tela MOSI (Master Out Slave In) e SDI (Serial Data In) 
TFT_CLK_PIN = const(6)  # Define o pino de clock para a tela (SCK Serial Clock)
'LED'
TFT_MISO_PIN = const(4)  # Define o pino de entrada de dados (MISO) para a tela (Master In Slave Out e SDO Serial Data Out)

#endregion


# ======================================================================
#  INICIO - UART para sensor do Rotametro
# ======================================================================
#region 
# Configuração do UART para sensor do Rotametro
uart = UART(1, baudrate=9600, rx=Pin(pino_rotametro))
#endregion


# ======================================================================
#  INICIO - Variaveis Globais e de controle
# ======================================================================
#region 
######### Variaveis Globais

# Conforme conf do inversor e motor
Rotacao_Max = 3550
Rotacao_Min = 1750
Rotacao_Fixa = 2420
Rotacao_Real = 0
Rotacao_Ideal = 2650

# Defina os ângulos mínimo e máximo do servo
Angulo_Min = 93 # Fechado
Angulo_Max = 175 # Aberto


posicao = 0 #Item escolhido Menu
Aguardando = True #para loop de forma temporaria
itens = None #Total de itens no menu
Acionado = False
Selecionado = None #Item selecionado no menu


# Valores padrão
VALORES_PADRAO = {
    "Rotacao_Max": 3550,
    "Rotacao_Min": 1750,
    "Rotacao_Fixa": 2420,
    "Rotacao_Ideal": 2650,
    "Angulo_Min": 93,
    "Angulo_Max": 175
}

# Variáveis que armazenam as configurações atuais
Rotacao_Max = VALORES_PADRAO["Rotacao_Max"]
Rotacao_Min = VALORES_PADRAO["Rotacao_Min"]
Rotacao_Fixa = VALORES_PADRAO["Rotacao_Fixa"]
Rotacao_Ideal = VALORES_PADRAO["Rotacao_Ideal"]
Angulo_Min = VALORES_PADRAO["Angulo_Min"]
Angulo_Max = VALORES_PADRAO["Angulo_Max"]


# ======================================================================
#  FIM - Variaveis Globais e de controle
# ======================================================================
#endregion



# ======================================================================
#  INICIO - Funções para salvar as variaveis no arquivo
# ======================================================================
#region

def carregar_configuracao():
    """Carrega as configurações do arquivo config.txt, se existir, senão usa os valores padrão."""
    global Rotacao_Max, Rotacao_Min, Rotacao_Fixa, Rotacao_Ideal, Angulo_Min, Angulo_Max
    try:
        with open('config.txt', 'r') as f:
            for linha in f:
                chave, valor = linha.strip().split('=')
                if chave in VALORES_PADRAO:
                    globals()[chave] = int(valor)  # Atualiza a variável global
        print("Configurações carregadas do arquivo.")
    except OSError:  # Corrigido para MicroPython
        print("Arquivo de configuração não encontrado. Usando valores padrão.")
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}. Usando valores padrão.")


def salvar_configuracao():
    """Salva as configurações atuais no arquivo config.txt"""
    try:
        with open('config.txt', 'w') as f:
            for chave in VALORES_PADRAO:
                f.write(f"{chave}={globals()[chave]}\n")
        print("Configurações salvas com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False


def restaurar_padrao():
    """Restaura os valores padrão e sobrescreve config.txt"""
    global Rotacao_Max, Rotacao_Min, Rotacao_Fixa, Rotacao_Ideal, Angulo_Min, Angulo_Max
    for chave, valor in VALORES_PADRAO.items():
        globals()[chave] = valor  # Atualiza as variáveis globais

    salvar_configuracao()  # Salva os valores padrão no arquivo
    print("Configurações restauradas para os valores padrão.")

# Carregar configurações na inicialização
carregar_configuracao()

#endregion



# ======================================================================
#  INICIO - Configuração da Tela
# ======================================================================
#region

######### Função para criar a tela
def MinhaTela():
    # Inicializa a interface SPI para a tela
    spiTFT = SPI(0, baudrate=20000000, sck=Pin(TFT_CLK_PIN), mosi=Pin(TFT_MOSI_PIN))
    
    # Cria uma instância da classe Display usando a interface SPI configurada
    tela = Display(spiTFT, dc=Pin(TFT_DC_PIN), cs=Pin(TFT_CS_PIN), rst=Pin(TFT_RST_PIN), rotation=180)
    
    return tela  # Retorna a instância do objeto tela criada

tela = MinhaTela()

########## Cores para a tela
Vermelho = ili9341.color565(255, 0, 0)
Verde = ili9341.color565(0, 255, 0)
Azul = ili9341.color565(0, 0, 255)
Amarelo = ili9341.color565(255, 255, 0)
Magenta = ili9341.color565(255, 0, 255)
Ciano = ili9341.color565(0, 255, 255)
Marrom = ili9341.color565(128, 0, 0)
VerdeEscuro = ili9341.color565(0, 128, 0)
AzulEscuro = ili9341.color565(0, 0, 128)
Oliva = ili9341.color565(128, 128, 0)
Roxo = ili9341.color565(128, 0, 128)
AzulClaro = ili9341.color565(0, 128, 128)
Cinza = ili9341.color565(128, 128, 128)
Prata = ili9341.color565(192, 192, 192)
Branco = ili9341.color565(255, 255, 255)
Preto = ili9341.color565(0, 0, 0)
Laranja = ili9341.color565(255, 165, 0)


####### Configurações da Tela
Fundo = Preto
Largura = 240
Altura = 320

Escrever = tela.draw_text # (x, y, text, font, color,  background=0,landscape=False, rotate_180=False, spacing=1)
Reta = tela.draw_line   # (x1, y1, x2, y2, color))
Retangulo = tela.draw_rectangle # Retangulo (x, y, largura, altura, cor)
Apaga = tela.fill_rectangle # Retangulo (x, y, w, h, color)
Imagem = tela.draw_image # (path, x=0, y=0, w=320, h=240)

# Limpa a tela
def Limpar():
    tela.clear(color=Fundo, hlines=10)

# Carrega a Fonte
Fonte1 = XglcdFont('fonts/Unispace12x24.c', 12, 24)

# Define a altura do título e o espaçamento entre as Linhas
Inicial = 40
Espacamento = 25

# Variáveis para Linhas
Linhas = [Inicial + (i * Espacamento)for i in range(20)]

# Defina a Margem e a largura do Caractere
Margem = 10
Caractere = 12

# Variáveis para representar Colunas
Colunas = [Margem + (i * Caractere) for i in range(20)]

# titulo
def Titulo(titulo):
    Escrever(Colunas[0]+9, 10, titulo, Fonte1, Branco, spacing=10)
#rodape
def Rodape(opcao):
    if opcao == 1:
        Escrever(Colunas[0]+5, Linhas[10], 'VOLTAR', Fonte1, Azul)
    elif opcao ==2:
        Escrever(Colunas[11], Linhas[10], 'AVANCAR', Fonte1, Azul)
    elif opcao == 3:
        Escrever(Colunas[0]+5, Linhas[10], 'VOLTAR', Fonte1, Azul)
        Escrever(Colunas[11], Linhas[10], 'AVANCAR', Fonte1, Azul)

# ======================================================================
#  FIM - Configuração da Tela
# ======================================================================
#endregion


# ======================================================================
#  INICIO - Funções de Controle e Auxiliares
# ======================================================================
#region

########VOLTAR#########
def Voltar():
    # Verifica se o botão de voltar foi pressionado
    if BT_Voltar.value() == 0:  # Se o botão de voltar for pressionado
        Botao_Debounce(BT_Voltar)
        return True
    return False
  
 ########OK#########  
def OK_Pressionado():
    # Verifica se o botão de OK foi pressionado
    if BT_Ok.value() == 0:  # Se o botão de OK for pressionado
        Botao_Debounce(BT_Ok)
        return True
    return False

##########POP_Up Mensagem##########
def Pop_Up_Mensagem(titulo, mensagem):
    """
    Exibe uma mensagem de pop-up com um título e uma mensagem.
    Fecha ao pressionar o botão Voltar ou OK.
    """
    
        # Exibe o título e a mensagem na tela
    Apaga(Colunas[0],Linhas[3], Largura-20, 130, Vermelho)
    posicao_coluna = Colunas[int((18 - len(titulo)) / 2)]  # Calcula a posição da coluna
    Escrever(posicao_coluna, Linhas[4], titulo, Fonte1, Amarelo, background=Vermelho)
    posicao_coluna_mensagem = Colunas[int((18 - len(mensagem)) / 2)]  # Calcula a posição da coluna
    Escrever(posicao_coluna_mensagem, Linhas[6], mensagem, Fonte1, Branco, background=Vermelho)
    while True:
        # Verifica se o botão de voltar foi pressionado
        if Voltar():
            Limpar()
            break
        
        utime.sleep(0.1)  # Pequeno atraso para evitar consumo excessivo de CPU

##########POP_Up Valor##########
def Pop_Up_Valor(tela, valor_inicial, titulo):
    """
    Tela parametrizada para ajustar valores.

    :param valor_inicial: Valor inicial (inteiro).
    :param titulo: Título a ser exibido na tela.
    :param callback_confirmar: Função a ser chamada ao confirmar o valor.
    :param callback_voltar: Função a ser chamada ao voltar.
    """
    Limpar()
    Titulo(tela)
    valor = valor_inicial
    posicao_digito = 0  # Começa no milhar (posição mais à esquerda)
    digitos = [int(d) for d in f"{valor:04d}"]  # Garante 4 dígitos
    
    # Apaga a área da tela e escreve o título
    Apaga(10, Linhas[5] - 25, Largura - 20, Espacamento * 4, Cinza)
    
    posicao_coluna = Colunas[int((18 - len(titulo)) / 2)]  # Calcula a posição da coluna
    Escrever(posicao_coluna, Linhas[5], titulo, Fonte1, Branco, background=Cinza)
    
    def Desenhar_Valor():
        """Mostra o valor atualizado e destaca o dígito selecionado."""
        Escrever(Colunas[7], Linhas[6], f"{''.join(map(str, digitos))}", Fonte1, Azul, background=Branco)
        posicoes_digitos = [Colunas[7], Colunas[8], Colunas[9], Colunas[10]]
        for i in range(4):
            cor = Branco if i == posicao_digito else Cinza
            Escrever(posicoes_digitos[i], Linhas[7], '^', Fonte1, cor, background=Cinza)

    Desenhar_Valor()  # Desenha o valor inicial

    while True:
        

        if BT_Cima.value() == 0:  # Incrementa o dígito atual
            digitos[posicao_digito] = (digitos[posicao_digito] + 1) % 10
            Desenhar_Valor()
            Botao_Debounce(BT_Cima)

        elif BT_Baixo.value() == 0:  # Decrementa o dígito atual
            digitos[posicao_digito] = (digitos[posicao_digito] - 1) % 10
            Desenhar_Valor()
            Botao_Debounce(BT_Baixo)

        elif BT_Direita.value() == 0:  # Próximo dígito à direita
            posicao_digito = (posicao_digito + 1) % 4
            Desenhar_Valor()
            Botao_Debounce(BT_Direita)

        elif BT_Esquerda.value() == 0:  # Próximo dígito à esquerda
            posicao_digito = (posicao_digito - 1) % 4
            Desenhar_Valor()
            Botao_Debounce(BT_Esquerda)

        elif BT_Ok.value() == 0:  # Confirma o valor
            valor_final = int(''.join(map(str, digitos)))
            print(f"Valor final ajustado: {valor_final}")
            break

        if Voltar():  # Verifica se o botão de voltar foi pressionado
            Apaga(10, Linhas[5] - 25, Largura - 20, Espacamento * 4, Fundo)
            return valor
        

        utime.sleep(0.1)  # Pequeno atraso para evitar loop excessivo
    Apaga(10, Linhas[5] - 25, Largura - 20, Espacamento * 4, Fundo)
    return valor_final

#####POTENCIOMETRO######
def ler_posicao_potenciometro(): # Retorna a posição do potenciômetro na escala de 0 a 100.
    valor_adc = Potenciometro.read_u16()  # Lê o valor do ADC (0 a 65535)
    posicao = round(((valor_adc * 100) / 65535),0)  # Converte para escala de 0 a 100
    return posicao

#########FUNCOES TELA##########

def Tela_Menu(): # Função para exibir o menu principal
    global Selecionado
    global Aguardando
    global itens
    Aguardando = True
    posicao = 0
    Limpar()
    Selecionado = 0   
    Titulo('###MENU###')

    # Dicionário que mapeia opções de menu
    menu_opcoes = {
        0: ('Rotacao Fixa', Tela_Rotacao_Fixa),
        1: ('Rotacao Manual', Tela_Rotacao_Manual),
        2: ('Automatico', Tela_Automatico),
        3: ('Sensor Mecanico', Tela_Sensor_Mecanico),
        4: ('Carga', Tela_Carga),
        5: ('Rotina', Tela_Rotina),
        6: ('Configurar', Tela_Configurar)
    }

        # Exibe o menu
    for chave, (texto, _) in menu_opcoes.items():
        Escrever(Colunas[0], Linhas[chave], texto, Fonte1, Verde)

    itens = len(menu_opcoes) - 1  # Define o número total de itens
    Seleciona(posicao)  # Destaca a posição inicial
    print("Menu Principal")

    while Aguardando:
        posicao = Teclado_Direcional(posicao)  # Atualiza a posição com base na entrada do teclado
        Seleciona(posicao)  # Destaca a nova posição
        
        

        # Chama a função correspondente se um item for selecionado
        if BT_Ok.value() == 0:  # Supondo que você tenha um botão para selecionar
            funcao = menu_opcoes.get(posicao, (None, None))[1]  # Obtém a função correspondente
            if funcao:  # Verifica se a função existe
                funcao()  # Chama a função
                Aguardando = False  # Para o loop após a seleção
        
        
        #####TEMPORARIO#####
        if Bt_Acionar.value() == 0:
            Tela_Configurar()
                
def Seleciona(posicao): # Função para selecionar um item no menu
    global Selecionado
    
    Retangulo(0, Linhas[posicao], Largura, Espacamento, Magenta)

    # Limpa o retângulo do item atualmente selecionado
    if Selecionado != posicao:  # Atualiza apenas se a posição mudou
        if Selecionado >= 0:  # Verifica se Selecionado é válido
            Retangulo(0, Linhas[Selecionado], Largura, Espacamento, Fundo)

        # Desenha o retângulo do novo item selecionado
        Retangulo(0, Linhas[posicao], Largura, Espacamento, Magenta)

        # Atualiza a seleção
        Selecionado = posicao
        
def Botao_Debounce(botao): # Função para aguardar o tempo de debounce após a liberação do botão
    debounce_time = 200  # Tempo mínimo entre acionamentos (em milissegundos)
    while botao.value() == 0:  # Aguarda até que o botão seja liberado
        utime.sleep_ms(debounce_time)  # Aguarda o tempo de debounce após a liberação
        
########## DIRECIONAL
def Teclado_Direcional(posicao):
    global itens
    if BT_Baixo.value() == 0:  # Verifica se o botão Baixo está pressionado
        Botao_Debounce(BT_Baixo)
        if posicao != itens:
            posicao += 1
        else:
            posicao = 0  # Se chegar ao último item, volta para o primeiro
        print(posicao)

    elif BT_Cima.value() == 0:  # Verifica se o botão Cima está pressionado
        Botao_Debounce(BT_Cima)
        if posicao != 0:
            posicao -= 1
        else:
            posicao = itens  # Se chegar ao primeiro item, volta para o último
        print(posicao)

    return posicao

def Bip(): # Função para emitir um bip
    print("BIP")
    return Tela_Menu()     
        
#####MEDIDOR DE RPM########
def medir_rpm(medidor: Pin, numero_amostras: int = 1, intervalo_ms: int = 500):
    contagem = 0
    tempos = []

    print("Iniciando medição de RPM...")
    while contagem < numero_amostras:
        if Voltar():  # Verifica a condição de interrupção antes de cada amostra
            return 0  # Encerra a função e retorna 0

        # Inicializa o contador de pulsos e marca o início do intervalo
        tempo_inicio = utime.ticks_ms()
        pulsos = 0

        # Conta os pulsos no intervalo de tempo especificado
        while utime.ticks_diff(utime.ticks_ms(), tempo_inicio) < intervalo_ms:
            if Voltar():  # Verifica a condição de interrupção dentro do loop
                return 0  # Encerra a função e retorna 0

            if medidor.value() == 0:  # Sensor detectou a borda de descida
                pulsos += 1
                # Aguarda o sensor voltar ao estado alto para evitar contar o mesmo pulso
                while medidor.value() == 0:
                    if Voltar():  # Verifica durante o loop de espera
                        return 0  # Encerra a função e retorna 0

        # Calcula a rotação por minuto a partir do número de pulsos no intervalo
        rpm = (pulsos * 60 * 1000) / intervalo_ms

        # Filtra valores fora da faixa
        if rpm != 0 and (rpm < 500 or rpm > 5000):
            print(f"Erro: RPM fora da faixa detectado: {rpm}")
            continue  # Ignora valores fora da faixa

        tempos.append(rpm)
        contagem += 1

    # Calcula a média dos valores de RPM
    if tempos:
        rpm_medio = sum(tempos) / len(tempos)
        return int(rpm_medio)
    else:
        return 0  # Retorna 0 caso nenhuma amostra válida tenha sido registrada

# ======================================================================
#  FIM - Funções de Controle e Auxiliares
# ======================================================================
#endregion

# ======================================================================
#  INICIO - Funções Principais
# ======================================================================
#region

######### FIXA ##########
def Tela_Rotacao_Fixa():
    print("Executando Rotação Fixa")
    global Rotacao_Fixa, Rotacao_Min, Rotacao_Max, Rotacao_Real, Acionado
    Servo.duty_ns(1516667)
    posicao_config = 0
    ciclo = 0  # Inicializa o ciclo para evitar erros
    tempo_ultimo_update = time.ticks_ms()  # Tempo inicial em milissegundos
    intervalo_atualizacao = 3000  # Intervalo de 3 segundos
    Acumulado = 0
    Ajuste = 0

    def calcular_duty(rotacao_fixa, rotacao_min, rotacao_max, ajuste=0):
        if rotacao_min <= rotacao_fixa <= rotacao_max:
            duty = int((rotacao_fixa - rotacao_min) * 65535 / (rotacao_max - rotacao_min))
        else:
            Pop_Up_Mensagem("ERRO", "Rotação fora da faixa válida")
            return 0  # Se fora da faixa, retorna 0, evitando valores inválidos

        duty += ajuste
        duty = max(0, min(65535, duty))  # Garante que o duty esteja entre 0 e 65535
        return duty

    def AtualizarTelaRotacao(rotacao_real, ciclo):
        # Atualiza a tela com a rotação real e o percentual de duty
        Escrever(Colunas[2], Linhas[5], f"{int(rotacao_real):04}", Fonte1, Azul, background=Branco)
        duty_percent = (ciclo * 100) // 65535  # Calcula a porcentagem de duty
        Escrever(Colunas[2], Linhas[7], f"{duty_percent:03}", Fonte1, Azul, background=Branco)

    def Desenhar_Tela(posicao_config):
        Escrever(Colunas[0], Linhas[2], '>>', Fonte1, Fundo)
        Escrever(Colunas[0], Linhas[3], '>>', Fonte1, Fundo)

        if posicao_config == 0:
            Escrever(Colunas[0], Linhas[2], '>>', Fonte1, Vermelho)
        elif posicao_config == 1:
            Escrever(Colunas[0], Linhas[3], '>>', Fonte1, Vermelho)

    def AtualizarTelaAcionado(acionado):
        if Acionado:
            Apaga(Colunas[0], Linhas[9], Largura - 40, Espacamento, Fundo)
            Escrever(Colunas[0], Linhas[9], '##CONTROLANDO##', Fonte1, Vermelho)
        else:
            Apaga(Colunas[0], Linhas[9], Largura - 40, Espacamento, Fundo)
            Escrever(Colunas[0], Linhas[9], '##MARCHA LENTA##', Fonte1, Vermelho)

    def Gera_Tela():
        Limpar()
        Titulo('###Fixa###')
        Escrever(Colunas[0], Linhas[1], 'Rotacao Solicitada', Fonte1, Verde)
        Escrever(Colunas[2], Linhas[2], str(Rotacao_Fixa), Fonte1, Azul, background=Branco)
        Escrever(Colunas[0], Linhas[4], 'Rotacao Real', Fonte1, Verde)
        Escrever(Colunas[0], Linhas[6], 'PWM', Fonte1, Verde)
        Escrever(Colunas[2], Linhas[3], 'Iniciar/Parar', Fonte1, Ciano)
        Desenhar_Tela(posicao_config)
        AtualizarTelaRotacao(Rotacao_Real, ciclo)
        AtualizarTelaAcionado(Acionado)
        Rodape(1)

    Gera_Tela()

    try:
        while True:
            # Checa o tempo passado
            tempo_atual = time.ticks_ms()
            if time.ticks_diff(tempo_atual, tempo_ultimo_update) >= intervalo_atualizacao:
                Rotacao_Real = medir_rpm(Sensor_RPM)  # Mede a rotação real
                tempo_ultimo_update = tempo_atual  # Atualiza o tempo do último update

                if Acionado:
                    if Rotacao_Real - Rotacao_Fixa > 50 and Rotacao_Real > Rotacao_Min:
                        Ajuste = -500 + Acumulado
                    elif Rotacao_Real - Rotacao_Fixa < -50 and Rotacao_Real > Rotacao_Min:
                        Ajuste = 500 + Acumulado
                    else:
                        Acumulado = 0
                        Ajuste = 0

                    ciclo = calcular_duty(Rotacao_Fixa, Rotacao_Min, Rotacao_Max, Ajuste)
                    PWM_Inversor.duty_u16(ciclo)  # Passando o valor de duty para PWM
                    AtualizarTelaRotacao(Rotacao_Real, ciclo)  # Atualiza na tela
                    print("duty ", ciclo, "Ajuste", Ajuste)
                else:
                    PWM_Inversor.duty_u16(0)

            if BT_Baixo.value() == 0:
                Botao_Debounce(BT_Baixo)
                posicao_config = (posicao_config + 1) % 2
                Desenhar_Tela(posicao_config)

            elif BT_Cima.value() == 0:
                Botao_Debounce(BT_Cima)
                posicao_config = (posicao_config - 1) % 2
                Desenhar_Tela(posicao_config)

            elif BT_Ok.value() == 0:
                Botao_Debounce(BT_Ok)
                try:
                    if posicao_config == 0:
                        novo_valor = Pop_Up_Valor('###Fixa###', Rotacao_Fixa, "Rotacao Fixa")
                        if Rotacao_Min <= novo_valor <= Rotacao_Max:
                            Rotacao_Fixa = novo_valor
                            if Acionado:
                                ciclo = calcular_duty(Rotacao_Fixa, Rotacao_Min, Rotacao_Max)
                                PWM_Inversor.duty_u16(ciclo)  # Passando o valor de duty para PWM
                            Gera_Tela()
                        else:
                            Pop_Up_Mensagem("INVALIDO", "FORA DA FAIXA")
                            Gera_Tela()
                    elif posicao_config == 1:
                        Acionado = not Acionado
                        if Acionado:
                            ciclo = calcular_duty(Rotacao_Fixa, Rotacao_Min, Rotacao_Max)
                            PWM_Inversor.duty_u16(ciclo)
                        else:
                            PWM_Inversor.duty_u16(0)
                            Rotacao_Real = 0
                            AtualizarTelaRotacao(Rotacao_Real, ciclo)  # Atualiza na tela
                        AtualizarTelaAcionado(Acionado)
                except Exception as e:
                    print(f"Erro ao processar a ação de 'Iniciar/Parar': {e}")

            if Voltar():
                break

    finally:
        PWM_Inversor.duty_u16(0)
        Acionado = False
        Tela_Menu()
        
########ROTACAO MANUAL########       
def Tela_Rotacao_Manual():
    global Rotacao_Min, Rotacao_Max, Rotacao_Real
    Servo.duty_ns(1516667)
    Rotacao_Real = 0
    tempo_ultimo_update = time.ticks_ms()  # Tempo inicial em milissegundos
    intervalo_atualizacao = 3000  # Intervalo de 3 segundos
    
    print("Executando Manual")
    Limpar()
    Titulo('##MANUAL##')
    Escrever(Colunas[0], Linhas[0], 'PWM', Fonte1, Verde)
    Escrever(Colunas[4], Linhas[1], '%', Fonte1, Branco)
    Escrever(Colunas[0], Linhas[2], 'Rotacao Calculada', Fonte1, Verde)
    Escrever(Colunas[0], Linhas[4], 'Rotacao Real', Fonte1, Verde)
    Rodape(1)


    # Checa a validade da configuração
    if Rotacao_Max < Rotacao_Min:
        Pop_Up_Mensagem("INVALIDO", "MAX < MIN")
        Tela_Configurar()
        return

    try:
        # Loop para ajuste do PWM e monitoramento do RPM
        while True:
            
            tempo_atual = time.ticks_ms()
            if time.ticks_diff(tempo_atual, tempo_ultimo_update) >= intervalo_atualizacao:
                Rotacao_Real = medir_rpm(Sensor_RPM)  # Mede a rotação real
                tempo_ultimo_update = tempo_atual  # Atualiza o tempo do último update

            # Ajusta o PWM e monitora a rotação
            posicao_potenciometro = ler_posicao_potenciometro()
            duty = int(posicao_potenciometro * 65535 / 100)  # Calcula o duty cycle pela posicao do pontenciometro
            PWM_Inversor.duty_u16(duty)
            
            # Verifica se o botão de voltar foi pressionado
            if Voltar():
                print("Botão voltar pressionado. Encerrando...")
                break
                   
            # Atualiza a rotação real na tela
            Escrever(Colunas[0], Linhas[1], f"{int(posicao_potenciometro):03}", Fonte1, Azul, background=Branco)
            Escrever(Colunas[0], Linhas[3], f"{int(((posicao_potenciometro*(Rotacao_Max-Rotacao_Min))/100) + Rotacao_Min):04}", Fonte1, Azul, background=Branco)
            Escrever(Colunas[0], Linhas[5], f"{int(Rotacao_Real):04}", Fonte1, Azul, background=Branco)
            
        
        
        utime.sleep(0.1)  # Pequeno atraso para evitar sobrecarga

    finally:
        # Desativa o monitoramento e desliga o PWM
        PWM_Inversor.duty_u16(0)
        Tela_Menu()

#########AUTOMATICO##########
def Tela_Automatico():
    print("Executando Automático")
    global Potenciometro, Servo
    Flutuador = 0
    Flutuador_Atual = 0
    LinhaX = 1
    Nivel_Solicitado = 1    
    Nivel_Solicitado_Atual = -1  # Inicializa com valor diferente de 0 a 9
    abertura_valvula = 0
    print("Aqui", Nivel_Solicitado)
    
    # Dicionário de posições com dicionários aninhados
    Posicao_Rotametro = {
        "SA": {"Flutuador": 1, "LinhaX": 8},
        "SB": {"Flutuador": 2, "LinhaX": 7},
        "SC": {"Flutuador": 3, "LinhaX": 6},
        "SD": {"Flutuador": 4, "LinhaX": 5},
        "SE": {"Flutuador": 5, "LinhaX": 4},
        "SF": {"Flutuador": 6, "LinhaX": 3},
        "SG": {"Flutuador": 7, "LinhaX": 2},
        "SH": {"Flutuador": 8, "LinhaX": 1},
        "SI": {"Flutuador": 9, "LinhaX": 0}
    }
    
    def calcular_duty_servo(abertura_valvula):
        # Calcula o duty cycle com base na abertura da válvula
        angulo = Angulo_Min + (abertura_valvula / 100) * (Angulo_Max - Angulo_Min)
        duty_ns = int(1000000 + (angulo / 180) * 1000000)
        return duty_ns
    
    def AtualizaTelaFlutuador():
        # Apaga os níveis superiores ao flutuador (invertido)
        for i in range(9):  
            Apaga(Colunas[15], Linhas[i], 30, 20, Fundo)  # Apaga o nível superior
        
        for linha in range(LinhaX, 9):  
            Apaga(Colunas[15], Linhas[linha], 30, 20, Vermelho)     
        
        Escrever(Colunas[15]+10, Linhas[9], str(Flutuador), Fonte1, Vermelho)
        
    def calcular_duty_motor():
        # Verifica se a rotação ideal está dentro da faixa válida
        if Rotacao_Min <= Rotacao_Ideal <= Rotacao_Max:
            # Calcula o duty cycle proporcional à rotação ideal
            duty_motor = int((Rotacao_Ideal - Rotacao_Min) * 65535 / (Rotacao_Max - Rotacao_Min))
        else:
            # Se a rotação estiver fora da faixa, exibe uma mensagem de erro e retorna 0
            Pop_Up_Mensagem("ERRO", "Rotação fora da faixa válida")
            return 0  # Retorna 0 para evitar valores inválidos

        # Garante que o duty esteja entre 0 e 65535
        duty_motor = max(0, min(65535, duty_motor))
        return duty_motor
    
    def Atualiza_Nivel():
        nonlocal  Nivel_Solicitado_Atual
        if Nivel_Solicitado != Nivel_Solicitado_Atual:
            Nivel_Solicitado_Atual = Nivel_Solicitado  # Atualiza a variável de controle do nível
            Escrever(Colunas[1], Linhas[9], str(Nivel_Solicitado), Fonte1, AzulClaro)

            # Apaga os níveis correspondentes
            for linha in range(9 - Nivel_Solicitado, 9):  
                Apaga(Colunas[0], Linhas[linha], 30, 20, AzulClaro)

            for i in range(9 - Nivel_Solicitado):
                Apaga(Colunas[0], Linhas[i], 30, 20, Fundo)
                
    def Atualiza_Mensagens():
        nonlocal Flutuador, LinhaX  # Adiciona as variáveis globais
        if uart.any():  # Verifica se há dados disponíveis no buffer UART
            ultima_mensagem = None
            while uart.any():  # Lê até que o buffer esteja vazio
                ultima_mensagem = uart.readline().decode().strip()  # Lê e decodifica a última linha            
                
            if ultima_mensagem:
                print(f"Mensagem recebida: {ultima_mensagem}")
                # Atualiza o valor do sensor se a mensagem estiver no dicionário
                if ultima_mensagem in Posicao_Rotametro:
                    Flutuador = Posicao_Rotametro[ultima_mensagem]["Flutuador"]
                    LinhaX = Posicao_Rotametro[ultima_mensagem]["LinhaX"]
                    print(f"Atualizado: Flutuador = {Flutuador}")
                        
                elif ultima_mensagem == "NA":
                    print("Nenhum sensor está ativo. Valor numérico inalterado.")
                        
                else:
                    print("Mensagem desconhecida. Valor numérico inalterado.")
                    
    def Atualiza_Controle():
        nonlocal abertura_valvula, Nivel_Solicitado, Flutuador, ciclo,ciclo_ideal, duty_ns

        if Nivel_Solicitado > Flutuador:
            if abertura_valvula < 100:
                Apaga(Colunas[3],Linhas[9],150,Espacamento,Fundo)
                abertura_valvula += 1 * (Nivel_Solicitado - Flutuador)
                abertura_valvula = min(abertura_valvula, 100)  # Garante limite
                duty_ns = calcular_duty_servo(abertura_valvula)
                Servo.duty_ns(duty_ns)
            else:
                if ciclo < 65535:
                    Apaga(Colunas[3],Linhas[9],150,Espacamento,Fundo)
                    ciclo += 500
                    ciclo = min(ciclo, 65535)  # Garante limite
                    PWM_Inversor.duty_u16(ciclo)
                else:
                    Escrever(Colunas[3], Linhas[9], '#SOBRECARGA', Fonte1, Branco, background=Vermelho)
                    
        elif Nivel_Solicitado < Flutuador:
            Apaga(Colunas[3],Linhas[9],150,Espacamento,Fundo)
            if abertura_valvula > 0:
                abertura_valvula -= 1 * (Flutuador-Nivel_Solicitado)
                abertura_valvula = max(abertura_valvula, 0)  # Garante limite
                duty_ns = calcular_duty_servo(abertura_valvula)
                Servo.duty_ns(duty_ns)
                if ciclo > ciclo_ideal:
                    ciclo -= 100
                    ciclo = max(ciclo, ciclo_ideal)  # Garante limite
                    PWM_Inversor.duty_u16(ciclo)
                    
            else:
                abertura_valvula = 0
                duty_ns = calcular_duty_servo(abertura_valvula)
                Servo.duty_ns(duty_ns)
                ciclo -= 100
                PWM_Inversor.duty_u16(ciclo)
                
                
        
        else:
            Apaga(Colunas[3],Linhas[9],150,Espacamento,Fundo)
            if ciclo > ciclo_ideal:
                ciclo -= 100
                ciclo = max(ciclo, ciclo_ideal)  # Garante limite
                PWM_Inversor.duty_u16(ciclo)    
            elif ciclo < ciclo_ideal:
                ciclo += 500
                ciclo = min(ciclo, ciclo_ideal)  # Garante limite
                PWM_Inversor.duty_u16(ciclo)
                                  

    Limpar()
    Titulo('###AUTO###')
    # Exibe as linhas do menu
    for i in range(9):
        Escrever(Colunas[5], Linhas[i], f'Nivel {9-i}', Fonte1, Verde)   
    Rodape(1)
    duty_ns = calcular_duty_servo(abertura_valvula)
    Servo.duty_ns(duty_ns)  
    print(f"Abertura da válvula: {abertura_valvula:.2f}%")
    ciclo_ideal = calcular_duty_motor()
    ciclo = ciclo_ideal
    
    PWM_Inversor.duty_u16(ciclo)


    try:
        while True:
            leitura_pot = Potenciometro.read_u16()
            Nivel_Solicitado = int((leitura_pot * 9) / 65535) + 1
            Nivel_Solicitado = min(Nivel_Solicitado,9)
            print("Solicitado", Nivel_Solicitado)
            print("valvula", abertura_valvula)
            
            Atualiza_Nivel()
            Atualiza_Mensagens()
            Atualiza_Controle()
                    
            if Flutuador != Flutuador_Atual:
                AtualizaTelaFlutuador()
                Flutuador_Atual = Flutuador

            # Verifica se o botão 'Voltar' foi pressionado
            if Voltar():
                print("Botão voltar pressionado. Encerrando...")
                break

            utime.sleep(0.1)  # Pequeno atraso para evitar loop excessivo

    except Exception as e:
        print(f"Erro inesperado: {e}")
        # Aqui você pode adicionar ações de fallback ou log adicional

    finally:
        # Desliga o PWM e o servo motor
        PWM_Inversor.duty_u16(0)
        Servo.duty_ns(1516667)
        Tela_Menu()

####### SENSOR MECÂNICO ########
def Tela_Sensor_Mecanico():
    print("Executando Sensor Mecanico")
    Limpar()
    Titulo('##SENSOR##')
    Rodape(1)
    estado_anterior = None  # Variável para armazenar o estado anterior do sensor
    
    
    try:
        while True:
            estado_atual = Sensor_Mecanico.value()
            
            if estado_atual != estado_anterior:  # Apenas atualiza se o estado mudar
                if estado_atual == 0:
                    print("Sensor Ativado")
                    Apaga(Colunas[0], Linhas[0], Largura - 20, Espacamento, Fundo)
                    Escrever(Colunas[0], Linhas[0], 'ATIVADO', Fonte1, Magenta)
                    Apaga(Colunas[0], Linhas[2], Largura - 20, Espacamento * 7, Vermelho)
                else:
                    print("Sensor Desativado")
                    Apaga(Colunas[0], Linhas[0], Largura - 20, Espacamento, Fundo)
                    Escrever(Colunas[0], Linhas[0], 'DESATIVADO', Fonte1, Magenta)
                    Apaga(Colunas[0], Linhas[2], Largura - 20, Espacamento * 7, VerdeEscuro)
                
                estado_anterior = estado_atual  # Atualiza o estado anterior
            
            if Voltar():
                print("Botão voltar pressionado. Encerrando...")
                break
            
            utime.sleep(0.1)

    finally:
        Tela_Menu()

##########CARGA##########
def Tela_Carga():
    print("Executando Carga")
    
    Limpar()
    Titulo('##CARGA##')
    Escrever(Colunas[2], Linhas[2], 'Liga', Fonte1, Verde)
    Escrever(Colunas[2], Linhas[4], 'Desliga', Fonte1, Vermelho)
    Rodape(1)
    
    posicao_config = 2  # Inicia com o indicador na opção "Liga"
    
    # Função para desenhar o indicador com base na posição
    def Desenhar_Tela(posicao_config):
        if posicao_config == 2:
            Escrever(Colunas[0], Linhas[2], '>>', Fonte1, Vermelho)  # Indica "Liga"
            Escrever(Colunas[0], Linhas[4], '>>', Fonte1, Fundo)     # Remove indicação de "Desliga"
            
        elif posicao_config == 4:
            Escrever(Colunas[0], Linhas[4], '>>', Fonte1, Vermelho)  # Indica "Desliga"
            Escrever(Colunas[0], Linhas[2], '>>', Fonte1, Fundo)     # Remove indicação de "Liga"
  
    
    # Inicializa a tela com o indicador na posição inicial
    Desenhar_Tela(posicao_config)
    
    try:
        while True:
            # Detecta botão para baixo
            if BT_Baixo.value() == 0:  
                posicao_config = 4  # Muda a posição para "Desliga"
                Desenhar_Tela(posicao_config)  # Atualiza a tela
                Botao_Debounce(BT_Baixo)  # Debounce para evitar leituras repetidas

            # Detecta botão para cima
            elif BT_Cima.value() == 0:  
                posicao_config = 2  # Muda a posição para "Liga"
                Desenhar_Tela(posicao_config)  # Atualiza a tela
                Botao_Debounce(BT_Cima)  # Debounce para evitar leituras repetidas

            # Detecta botão OK
            elif BT_Ok.value() == 0:  
                if posicao_config == 2:  # Liga a lâmpada
                    Lampada.value(1) 
                    Escrever(Colunas[2], Linhas[2], 'Liga', Fonte1, Vermelho)
                    Escrever(Colunas[2], Linhas[4], 'Desliga', Fonte1, Verde)
                    Apaga(Colunas[3], Linhas[6], Largura - 100, Espacamento*3, Branco)
                    print("Liga")
                elif posicao_config == 4:  # Desliga a lâmpada
                    Lampada.value(0)
                    Escrever(Colunas[2], Linhas[2], 'Liga', Fonte1, Verde)
                    Escrever(Colunas[2], Linhas[4], 'Desliga', Fonte1, Vermelho)
                    Apaga(Colunas[3], Linhas[6], Largura - 100, Espacamento*3, Fundo)
                    print("Desliga")
                Botao_Debounce(BT_Ok)  # Debounce para evitar leituras repetidas

            # Detecta botão voltar
            if Voltar():
                print("Botão voltar pressionado. Encerrando...")
                break

            utime.sleep(0.05)  # Pequena pausa para evitar uso excessivo de CPU

    finally:
        Lampada.value(0)  # Garante que a lâmpada seja desligada ao sair
        Tela_Menu()
    
        
#######TELA ROTINA########
def Tela_Rotina():
    print("Executando Rotina")
    global Potenciometro, Servo
    Flutuador = 0
    Abertura_Valvula = 0

    # Dicionário de posições com dicionários aninhados
    Posicao_Rotametro = {
        "SA": {"Flutuador": 1, "LinhaX": 8},
        "SB": {"Flutuador": 2, "LinhaX": 7},
        "SC": {"Flutuador": 3, "LinhaX": 6},
        "SD": {"Flutuador": 4, "LinhaX": 5},
        "SE": {"Flutuador": 5, "LinhaX": 4},
        "SF": {"Flutuador": 6, "LinhaX": 3},
        "SG": {"Flutuador": 7, "LinhaX": 2},
        "SH": {"Flutuador": 8, "LinhaX": 1},
        "SI": {"Flutuador": 9, "LinhaX": 0}
    }

    def calcular_duty_motor(Rotacao_Motor):
        duty_motor = int((Rotacao_Motor - Rotacao_Min) * 65535 / (Rotacao_Max - Rotacao_Min))
        return max(0, min(65535, duty_motor))

    def calcular_duty_servo(abertura_valvula):
        angulo = Angulo_Min + (abertura_valvula / 100) * (Angulo_Max - Angulo_Min)
        return int(1000000 + (angulo / 180) * 1000000)

    def Atualiza_Flutuador():
        print('iniciado flutuador')
        nonlocal Flutuador
        if uart.any():
            ultima_mensagem = None
            while uart.any():
                ultima_mensagem = uart.readline().decode().strip()

            if ultima_mensagem:
                print(f"Mensagem recebida: {ultima_mensagem}")
                if ultima_mensagem in Posicao_Rotametro:
                    Flutuador = Posicao_Rotametro[ultima_mensagem]["Flutuador"]
                elif ultima_mensagem == "NA":
                    print("Nenhum sensor está ativo. Valor numérico inalterado.")
                else:
                    print("Mensagem desconhecida. Valor numérico inalterado.")
                    
            utime.sleep(0.1)

    def Atualiza_Rotametro(nivel):
        nonlocal Flutuador, Abertura_Valvula, ciclo

        while nivel != Flutuador:
            print(Flutuador, "solicita = ", nivel)
            print("valvula ", Abertura_Valvula )
            if nivel > Flutuador:
                if Abertura_Valvula < 100:
                    Abertura_Valvula += (nivel - Flutuador)
                    Abertura_Valvula = min(100, Abertura_Valvula)
                else:
                    ciclo = min(ciclo + 500, 65535)
                    PWM_Inversor.duty_u16(ciclo)
            else:
                if Abertura_Valvula > 0:
                    Abertura_Valvula -= (Flutuador - nivel)
                    Abertura_Valvula = max(0, Abertura_Valvula)
                else:
                    ciclo = max(ciclo - 500, 0)
                    PWM_Inversor.duty_u16(ciclo)

            Servo.duty_ns(calcular_duty_servo(Abertura_Valvula))
            print("chama flutuador")
            Atualiza_Flutuador()
            if Voltar():
                Encerrar()

    def Tempo_Espera(tempo):
        inicio = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), inicio) < tempo * 1000:
            if Voltar():
                Encerrar()

    def Espera_Sensor():
        while True:
            if Sensor_Mecanico.value() == 0:
                break
            
            if Voltar():
                Encerrar()

    
    def Encerrar():
        Lampada.value(0)
        Servo.duty_ns(1516667)
        PWM_Inversor.duty_u16(0)
        Tela_Menu()
        

    Limpar()
    Titulo('##ROTINA##')
    Rodape(1)

    try:
        while True:
            print("INICIO DO WHILE TRUE")
            Servo.duty_ns(calcular_duty_servo(0))
            ciclo = calcular_duty_motor(1800)
            PWM_Inversor.duty_u16(ciclo)
            
            if Voltar():
                print("Botão voltar pressionado. Encerrando...")
                break

            Apaga(Colunas[0], Linhas[0], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[2], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[3], Largura-20, Espacamento, Fundo)
            Escrever(Colunas[3], Linhas[0], 'PASSO #1', Fonte1, Vermelho)
            Escrever(Colunas[0], Linhas[2], 'Ajustando', Fonte1, Verde)
            Escrever(Colunas[2], Linhas[3], 'para 2800 rpm', Fonte1, Verde)

            ciclo = calcular_duty_motor(2800)
            PWM_Inversor.duty_u16(ciclo)
            rpm_atual = medir_rpm(Sensor_RPM)  # Mede a rotação real
            Escrever(Colunas[5], Linhas[5], 'RPM', Fonte1, Ciano)
            Escrever(Colunas[5], Linhas[6], f"{int(rpm_atual):04}", Fonte1, Azul, background=Branco)
            while not (2720 <= rpm_atual <= 2880):
                if rpm_atual < 2800:
                    ciclo = min(ciclo + 100, 65535)
                    PWM_Inversor.duty_u16(ciclo)
                if rpm_atual > 2800:
                    ciclo = max(ciclo -100,0)
                    PWM_Inversor.duty_u16(ciclo)
                rpm_atual = medir_rpm(Sensor_RPM)
                Escrever(Colunas[5], Linhas[6], f"{int(rpm_atual):04}", Fonte1, Azul, background=Branco)
                if Voltar():
                    Encerrar()
                utime.sleep(0.1)
                        
            Escrever(Colunas[5], Linhas[6], f"{int(rpm_atual):04}", Fonte1, Azul, background=Branco)            
            Tempo_Espera(5)
            #verifica a rpm
            
            if Voltar():
                print("Botão voltar pressionado. Encerrando...")
                break
            
            Apaga(Colunas[0], Linhas[5], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[6], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[0], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[2], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[3], Largura-20, Espacamento, Fundo)
            Escrever(Colunas[3], Linhas[0], 'PASSO #2', Fonte1, Vermelho)
            Escrever(Colunas[0], Linhas[2], 'Ajustando', Fonte1, Verde)
            Escrever(Colunas[2], Linhas[3], 'para nivel 3', Fonte1, Verde)           
            Atualiza_Rotametro(3)
            Tempo_Espera(5)
            
            if Voltar():
                print("Botão voltar pressionado. Encerrando...")
                break
            
            
            Apaga(Colunas[0], Linhas[0], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[2], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[3], Largura-20, Espacamento, Fundo)
            Escrever(Colunas[3], Linhas[0], 'PASSO #3', Fonte1, Vermelho)
            Escrever(Colunas[0], Linhas[2], 'Ajustando', Fonte1, Verde)
            Escrever(Colunas[2], Linhas[3], 'para nivel 7', Fonte1, Verde)
            Escrever(Colunas[2], Linhas[4], 'Lampada ON', Fonte1, Ciano) 
            Lampada.value(1)
            Atualiza_Rotametro(7)
            
            Tempo_Espera(5)
            
            Apaga(Colunas[0], Linhas[0], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[2], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[3], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[4], Largura-20, Espacamento, Fundo)
            Escrever(Colunas[3], Linhas[0], 'PASSO #4', Fonte1, Vermelho)
            Escrever(Colunas[0], Linhas[2], 'Esperando', Fonte1, Verde)
            Escrever(Colunas[2], Linhas[3], 'Fim de Curso', Fonte1, Verde)
            Espera_Sensor()
            
            Apaga(Colunas[0], Linhas[0], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[2], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[3], Largura-20, Espacamento, Fundo)
            Escrever(Colunas[3], Linhas[0], 'PASSO #5', Fonte1, Vermelho)
            Escrever(Colunas[0], Linhas[2], 'Ajustando', Fonte1, Verde)
            Escrever(Colunas[2], Linhas[3], 'para nivel 4', Fonte1, Verde)
            Atualiza_Rotametro(4)
            
            Tempo_Espera(5)
            
            Apaga(Colunas[0], Linhas[0], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[2], Largura-20, Espacamento, Fundo)
            Apaga(Colunas[0], Linhas[3], Largura-20, Espacamento, Fundo)
            Escrever(Colunas[3], Linhas[0], 'PASSO #6', Fonte1, Vermelho)
            Escrever(Colunas[2], Linhas[2], 'Lampada OFF', Fonte1, Ciano)
            Escrever(Colunas[2], Linhas[3], 'Reiniciando', Fonte1, Verde) 
            Lampada.value(0)
            Servo.duty_ns(calcular_duty_servo(0))
            PWM_Inversor.duty_u16(calcular_duty_motor(1800))
            
            Tempo_Espera(5)
            
            if Voltar():
                print("Botão voltar pressionado. Encerrando...")
                break

    finally:
        Lampada.value(0)
        Servo.duty_ns(1516667)
        PWM_Inversor.duty_u16(0)
        Tela_Menu()
                
#######TELA CONFIGURAR######
def Tela_Configurar():
    print("Executando Rotação Fixa")
    global Rotacao_Max, Rotacao_Min, Rotacao_Fixa, Rotacao_Ideal, Angulo_Min, Angulo_Max
    
    posicao_config = 1
    tela = 1
    
 
    
    def Gera_Tela_1():
        nonlocal posicao_config
        Limpar()
        Titulo('Configurar')
        Rodape(3)
        Escrever(Colunas[0], Linhas[0], 'Rotacao Min', Fonte1, Verde)
        Escrever(Colunas[2], Linhas[1], f"{int(Rotacao_Min):04}", Fonte1, Azul, background=Branco)        
        Escrever(Colunas[0], Linhas[2], 'Rotacao Max', Fonte1, Verde)
        Escrever(Colunas[2], Linhas[3], f"{int(Rotacao_Max):04}", Fonte1, Azul, background=Branco)
        Escrever(Colunas[0], Linhas[4], 'Rotacao Ideal', Fonte1, Verde)
        Escrever(Colunas[2], Linhas[5], f"{int(Rotacao_Ideal):04}", Fonte1, Azul, background=Branco)
        Escrever(Colunas[0], Linhas[6], 'Rotacao Fixa', Fonte1, Verde)
        Escrever(Colunas[2], Linhas[7], f"{int(Rotacao_Fixa):04}", Fonte1, Azul, background=Branco)
        Escrever(Colunas[3], Linhas[8], 'Persistente', Fonte1, Amarelo)
        Escrever(Colunas[3], Linhas[9], 'Restaurar', Fonte1, Laranja)
        Atualiza_Tela_1(posicao_config)
        
    def Gera_Tela_2():
        nonlocal posicao_config
        print("tela 2")
        Limpar()
        Titulo('Configurar')
        Rodape(1)
        Escrever(Colunas[2], Linhas[0], 'Ajuste Valvula', Fonte1, Ciano)
        Escrever(Colunas[0], Linhas[2], 'Angulo Min', Fonte1, Verde)
        Escrever(Colunas[2], Linhas[3], f"{int(Angulo_Min):03}", Fonte1, Azul, background=Branco)        
        Escrever(Colunas[0], Linhas[5], 'Rotacao Max', Fonte1, Verde)
        Escrever(Colunas[2], Linhas[6], f"{int(Angulo_Max):03}", Fonte1, Azul, background=Branco)
        Atualiza_Tela_2()
        
    def Atualiza_Tela_2():
        nonlocal posicao_config
        if posicao_config == 1:
            posicao_config = 2
            Escrever(Colunas[0], Linhas[3], '>>', Fonte1, Fundo)
            Escrever(Colunas[0], Linhas[6], '>>', Fonte1, Vermelho)
        else:
            posicao_config = 1
            Escrever(Colunas[0], Linhas[6], '>>', Fonte1, Fundo)
            Escrever(Colunas[0], Linhas[3], '>>', Fonte1, Vermelho)
    
    def Atualiza_Tela_1(item):
        # Remove o indicador >> de todas as linhas (desenha com a cor de fundo)
        for linha in [1, 3, 5, 7, 8, 9]:
            Escrever(Colunas[0], Linhas[linha], '>>', Fonte1, Fundo)  # Apaga o indicador
        
        # Desenha o indicador >> na linha selecionada
        linhas_posicoes = {1: 1, 2: 3, 3: 5, 4: 7, 5: 8, 6: 9}
        linha_indicador = linhas_posicoes.get(item, 1)
        Escrever(Colunas[0], Linhas[linha_indicador], '>>', Fonte1, Vermelho)

    Gera_Tela_1()
    
    try:
        while True:              
                
                if BT_Cima.value()==0:  # Verifica se o botão "Cima" foi pressionado
                    Botao_Debounce(BT_Cima)
                    posicao_config = 6 if posicao_config == 1 else posicao_config - 1
                    Atualiza_Tela_1(posicao_config)
                
                if BT_Baixo.value()==0:  # Verifica se o botão "Baixo" foi pressionado
                    Botao_Debounce(BT_Baixo)
                    posicao_config = 1 if posicao_config == 6 else posicao_config + 1
                    Atualiza_Tela_1(posicao_config)
                    
                    
                if BT_Direita.value() == 0:
                    Botao_Debounce(BT_Direita)
                    posicao_config = 2
                    tela = 2
                    
                if BT_Ok.value() == 0:
                    Botao_Debounce(BT_Ok)
                    
                    if posicao_config == 1:
                        Rotacao_Min = Pop_Up_Valor('Configurar', Rotacao_Min, "Rotacao Min")
                    elif posicao_config == 2:
                        Rotacao_Max = Pop_Up_Valor('Configurar', Rotacao_Max, "Rotacao Max")
                    elif posicao_config == 3:
                        Rotacao_Ideal = Pop_Up_Valor('Configurar', Rotacao_Ideal, "Rotacao Ideal")
                    elif posicao_config == 4:
                        Rotacao_Fixa = Pop_Up_Valor('Configurar', Rotacao_Fixa, "Rotacao Fixa")
                    elif posicao_config == 5:
                        Persistente = salvar_configuracao()
                        Apaga(Colunas[0],Linhas[3], Largura-20, 130, AzulClaro)
                        Escrever(Colunas[6], Linhas[4], 'Salvo', Fonte1, Branco, background=AzulClaro)
                        Escrever(Colunas[2], Linhas[6], 'Dados Gravados', Fonte1, Branco, background=AzulClaro)
                        utime.sleep(3)
                        Apaga(Colunas[0],Linhas[3], Largura-20, 130, Fundo)
                        
                    elif posicao_config == 6:
                        Restaurar = carregar_configuracao()
                        Apaga(Colunas[0],Linhas[3], Largura-20, 130, AzulClaro)
                        Escrever(Colunas[4], Linhas[4], 'Carregado', Fonte1, Branco, background=AzulClaro)
                        Escrever(Colunas[1], Linhas[6], 'Dados Carregados', Fonte1, Branco, background=AzulClaro)
                        utime.sleep(3)
                        Apaga(Colunas[0],Linhas[3], Largura-20, 130, Fundo)
                    Gera_Tela_1()
                        
                        
                if Voltar():  # Verifica se o botão "Voltar" foi pressionado
                    if Rotacao_Max < Rotacao_Min:
                        Pop_Up_Mensagem("INVALIDO", "MAX < MIN")  # Exibe mensagem de erro
                        
                    elif not (Rotacao_Min <= Rotacao_Fixa <= Rotacao_Max) or not (Rotacao_Min <= Rotacao_Ideal <= Rotacao_Max):
                        Pop_Up_Mensagem("INVALIDO", "VERIFIQUE")  # Exibe outra mensagem de erro
                        
                    else:
                        break  # Caso contrário, sai do loop
                        

                    # Atualiza a tela após a alteração
                    Gera_Tela_1()
                    Rodape(3)
                    Atualiza_Tela_1(posicao_config)

                        
      

                
                time.sleep(0.1)  # Pequeno delay para evitar leitura múltipla do botão
            
                if tela == 2:
                    Gera_Tela_2()
                    while tela == 2:    
                        if BT_Cima.value()==0:  # Verifica se o botão "Cima" foi pressionado
                            Botao_Debounce(BT_Cima)
                            Atualiza_Tela_2()

                        
                        if BT_Baixo.value()==0:
                            Botao_Debounce(BT_Baixo)
                            Atualiza_Tela_2()
                        
                        if BT_Ok.value() == 0:
                            Botao_Debounce(BT_Ok)
                            if posicao_config == 1:
                                Angulo_Min = Pop_Up_Valor('Configurar', Angulo_Min, "Angulo Min")
                                Gera_Tela_2()
                            elif posicao_config == 2:
                                Angulo_Max = Pop_Up_Valor('Configurar', Angulo_Max, "Angulo Max")
                                Gera_Tela_2()

                        
                        if Voltar():
                            tela =1
                            posicao_config = 1
                            Gera_Tela_1()
                                    
                            
    
    finally:
        Tela_Menu()  # Retorna ao menu principal após sair do loop

#endregion  
    

# Chama a tela inicial
Tela_Menu()
