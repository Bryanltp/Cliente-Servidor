import socket
from time import *
from Pacote import *
import pickle
import os


def decodifica_dicio(dados_json):
    pack = Pacote()
    pack.set_num_seq(dados_json["num_seq"])
    pack.set_dados(dados_json["data"])
    pack.set_sender_adress(dados_json["sender_adress"])
    pack.set_receiver_adress(dados_json["receiver_adress"])
    pack.set_sended(dados_json["sended"])
    pack.set_sended_time(dados_json["sended_time"])
    pack.set_last(dados_json["last"])
    return pack

# Função que recebe os dados lidos no arquivo para envio e cria o pacote para envio


def gera_paco(data, i, addr, fim):
    pack = Pacote()
    pack.set_num_seq(bin(i))
    pack.set_dados(data)
    pack.set_sender_adress(('localhost', 1998))
    pack.set_receiver_adress(addr)
    pack.set_sended(True)
    pack.set_sended_time(time())
    pack.set_last(fim)
    return pack


# Verifica se o Número de sequência é diferente. Retorna True caso seja.
def verifica_ack(received_pack, i):
    return received_pack.get_num_seq() != bin(i)


def envia_arquivo(server, addr, nome):
    # Define time out em segundos
    server.settimeout(time_out)
    # Arquivo de envio - Se não existir sai da conexão
    try:
        file = open("./servidor/"
                    + nome, "rb")
    except FileNotFoundError:
        return
    # Referência do seq_number
    i = 0
    fim = False
    resending = False
    data = 0
    cont_loss_pack = 0
    try:
        while True:
            # Pergunta se o dado final
            if not resending:
                data = file.read(buffer)
            size = len(data)
            # Indica que é o último arquivo
            if size < buffer:
                fim = True
            # 1 Cria pacote
            pack = gera_paco(data, i, addr, fim)
            # Converte pacote em dicionário
            pack_dict = pack.__dict__
            pack_dict = pickle.dumps(pack_dict)   # Serial

            # 2 Enviando o pacote
            server.sendto(bytes(pack_dict), addr)
            # 3 Wait  recebe o pacote
            received_ack, addr = server.recvfrom(1024)
            # Converte para dict
            received_ack = pickle.loads(received_ack)
            # Decodifica Ack para objeto <Pacote> recebendo pacote do ack do cliente
            received_ack = decodifica_dicio(received_ack)
            # Verifica se ele é o ACK esperado      4 - Verifica pacote
            if verifica_ack(received_ack, i):
                print("ACK modificado. Reenviando")
                resending = True
                cont_loss_pack = cont_loss_pack + 1
            else:
                # else: calcular o RTT  e seta o num_seq
                rtt_envio.append(time() - received_ack.get_sended_time())
                i = i + 1
                resending = False
            # Se foi o último pacote e ele foi recebido corretamente, saí do laço
            if fim:
                print("Concluído!")
                cont_pack = i
                break

        print("Pacotes: ", cont_pack)
        print("Pacotes perdidos: ", cont_loss_pack)
        file.close()
    except socket.timeout:
        pass


# Configurações do server
host = "localhost"
# Tamanho dos dados para envio
buffer = 512  # 512 bytes
time_out = 5  # 5s
senha = "54321"
rtt_envio = []
rtt_recebimento = []

if __name__ == '__main__':

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Tipo UDP/IP
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 1998))
    print("Server Iniciado")

    while True:

        server.settimeout(5000)
        # Solicitação do cliente
        msg, addr = server.recvfrom(1024)
        print("Cliente conectado")
        # Porta do cliente.
        print("IP: ", addr)

        # Função que envia os arquivos presentes no sistema e opção de baixar ou enviar
        list_files = os.listdir("./servidor/")

        files = ''

        # Concatena
        for file in list_files:
            files = files + file + '\n'

        # Enviando as opções para o cliente
        server.sendto(bytes(files, encoding='utf-8'), addr)
        name_file, addr = server.recvfrom(1024)
        name_file = name_file.decode('utf-8')
        envia_arquivo(server, addr, name_file)
