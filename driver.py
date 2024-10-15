import tkinter as tk
import socket
import struct

class Driver:
    def __init__(self, host_ip: str, port: int, unit_id: int = 1) -> None:
        self.host_ip = host_ip
        self.port = port
        self.unit_id = unit_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host_ip, self.port))

    def __create_message(self, transaction_id, function_code, address, value):
        protocol_id_modbus = 0
        length = 6
        header = struct.pack('>HHHB', transaction_id, protocol_id_modbus, length, self.unit_id)
        body = struct.pack('>BHH', function_code, address, value)
        return header + body

    def send_action_button(self, address: int, value: bool):
        try:
            modbus_value = 0xFF00 if value else 0x0000
            request = self.__create_message(1, 0x05, address, modbus_value)
            self.socket.sendall(request)

            response = self.socket.recv(1024)
            print(f"Tamanho da resposta: {len(response)} bytes")
            print(f"Resposta bruta: {response}")

            if len(response) < 9:
                raise ValueError("Resposta incompleta, verifique a conexão ou o dispositivo.")

            transacao, protocolo, tamanho, unidade = struct.unpack('>HHHB', response[:7])
            funcao = response[7]

            if funcao > 0x80:
                codigo_excecao = response[8]
                print(f"Erro Modbus: Função {hex(funcao)}, Código de exceção: {hex(codigo_excecao)}")
                if codigo_excecao == 0x02:
                    print("Exceção 0x02: Illegal Data Address. Verifique o endereço do coil.")
                return

            endereco, valor = struct.unpack('>HH', response[8:12])

            print(f"Transação: {transacao}, Protocolo: {protocolo}, Tamanho: {tamanho}, Unidade: {unidade}")
            print(f"Função: {funcao}, Endereço: {endereco}, Valor: {valor}")

            if funcao == 0x05 and endereco == address and valor == modbus_value:
                print(f"Coil {address} atualizado com sucesso.")
            else:
                print(f"Erro ao atualizar o coil {address}, verifique a resposta.")

        except Exception as e:
            print(f"Erro: {e}")

    def close_socket(self):
        self.socket.close()


