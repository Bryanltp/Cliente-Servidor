from socket import *
from Pacote import *
from time import *
import random as rdm
import pickle

# Função para simular uma perda de 10% dos ACKs


def simula_perda_de_ack(pack_ack):
    if rdm.random() > 0.5:
        # TESTE: DEIXANDO PACOTES SE PERDER
        pack_ack.set_num_seq(bin(-1))
    return pack_ack


def decodifica_dicio(dados_json):
    # dados_json = json.loads(dados_json)
    pack = Pacote()
    pack.set_num_seq(dados_json["num_seq"])
    # Não retorna os dados, apenas os parâmetros
    pack.set_dados(dados_json["data"])
    pack.set_sender_adress(dados_json["sender_adress"])
    pack.set_receiver_adress(dados_json["receiver_adress"])
    pack.set_sended(dados_json["sended"])
    pack.set_sended_time(dados_json["sended_time"])
    pack.set_last(dados_json["last"])
    return pack

# Setando atributos do ACK
# Adiciona no Objeto <Pacote> as informações do ACK


def cria_ack_do_pacote(pack, received_time):
    # Salva o tempo de recebimento no cliente
    pack.set_received_time(received_time)
    # Informa que o pacote foi recebido
    pack.set_received(True)
    return pack

# Envia ao server um pedido do arquivo


def pede_server(conexaoSocket, adrr):
    conexaoSocket.sendto("SYN. Cliente 1".encode('utf-8'), adrr)

# Envia ACK confirmando o recebimento do pacote


def envia_ack(conexaoSocket, pack_ack, adrr):
    # Exclui dados no envio do ACK
    pack_ack.set_dados(None)
    # Converte para dicionário e serializa os dados
    pack_serial = pickle.dumps(pack_ack.__dict__)
    # Envia Json
    conexaoSocket.sendto(bytes(pack_serial), adrr)


# Função que recebe o pacote enviado pelo server
def recebe_servidor(conexaoSocket):
    datagrama, adrr = conexaoSocket.recvfrom(1024)
    received_time = time()
    # Passando para dict novamente
    datagrama = pickle.loads(datagrama)
    # Decodificando o pacote recebido para Objeto <Pacote>
    pack = decodifica_dicio(datagrama)
    # Criando o ACK
    pack_ack = cria_ack_do_pacote(pack, received_time)
    return pack_ack, adrr


# Função que salva os dados recebidos
def salvando_dados(data, nome):
    file = open("./cliente/" +
                nome, "wb")
    for d in data:
        file.write(d)
    file.close()


def recebendo_arquivo(conexaoSocket, nome):
    i = 0
    data = []
    while True:
        # Recebe parte do arquivo. Se o envio do ack falhar ele retorna a esse mesmo ponto.
        pack_ack, adrr = recebe_servidor(conexaoSocket)

        simula_perda_de_ack(pack_ack)

        # Se o número de sequência for o que estamos esperando, salva os dados e passa para o próximo.
        if pack_ack.get_num_seq() == bin(i):
            # Salva dados recebidos em uma lista
            data.append(pack_ack.get_dados())
            # Proximo seq_number
            i = i + 1

        # Envia ACK. Remove dados antes do envio.
        envia_ack(conexaoSocket, pack_ack, adrr)
        # Se for o último pacote sai do laço        *** tratar caso do ultimo pacote
        if pack_ack.get_last():
            break
    # Salva o arquivo recebido
    salvando_dados(data, nome)
    print("\n>>>>Arquivo recebido com sucesso!<<<<\n")


# Função que recebe a lista de arquivos disponíveis
def recebendo_lista_e_opcoes(conexaoSocket):
    # Recebe a lista de arquivos e opções
    msg, adrr = conexaoSocket.recvfrom(1024)
    msg = msg.decode('utf-8')
    print("------------------------------------")
    print("---------LISTA DE ARQUIVOS----------")
    print(msg)
    return msg

# Envia nome do arquivo para download/envio


def seleciona_nome(conexaoSocket, adrr, opcoes):
    while True:
        print("------------------------------------")
        nome = input("Selecione o arquivo para download: ")
        if nome not in opcoes:
            print(">>>>>Erro no nome digitado")
        else:
            break
    conexaoSocket.sendto(nome.encode('utf-8'), adrr)
    return nome


# Dados para conexão com servidor
host = "localhost"  # IP do Servidor
port = 1998
time_out = 5
buffer = 512

if __name__ == '__main__':
    # Configurações do socket. AF_INET = IP, SOCK_STREAM = TCP e SOCK_DGRAM = UDP
    conexaoSocket = socket(AF_INET, SOCK_DGRAM)  # Tipo UDP/IP

    # Envia pedido de lista das opções do server
    pede_server(conexaoSocket, (host, port))
    # Recebe arquivos disponíveis e opções
    opcoes = recebendo_lista_e_opcoes(conexaoSocket)
    # Envia nome do arquivo para envio/download
    nome = seleciona_nome(conexaoSocket, (host, port), opcoes)

    recebendo_arquivo(conexaoSocket, nome)
    conexaoSocket.close()
