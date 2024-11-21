import socket
import struct
import random
class Driver:
    def __init__(self, host_ip: str, port: int, unit_id: int = 1) -> None:
        self.host_ip = host_ip
        self.port = port
        self.unit_id = unit_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host_ip, self.port))

    def __create_message(self, transaction_id, function_code, address, quantity):
        protocol_id_modbus = 0
        length = 6
        header = struct.pack('>HHHB', transaction_id, protocol_id_modbus, length, self.unit_id)
        body = struct.pack('>BHH', function_code, address, quantity)
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

    def read_coil(self, address: int, quantity: int = 1):
        """
        Lê o estado de um ou mais coils.
        
        :param address: Endereço inicial do coil.
        :param quantity: Quantidade de coils para ler.
        :return: Lista de estados dos coils (True/False).
        """
        try:
            transaction_id = random.randint(0, 65535)  # Transação única (pode ser incrementada ou aleatória)
            request = self.__create_message(transaction_id, 0x01, address, quantity)
            self.socket.sendall(request)

            response = self.socket.recv(1024)
            print(f"Tamanho da resposta: {len(response)} bytes")
            print(f"Resposta bruta: {response}")

            if len(response) < 9:
                raise ValueError("Resposta incompleta, verifique a conexão ou o dispositivo.")

            # Processar cabeçalho
            transacao, protocolo, tamanho, unidade = struct.unpack('>HHHB', response[:7])
            funcao = response[7]

            if funcao > 0x80:
                codigo_excecao = response[8]
                print(f"Erro Modbus: Função {hex(funcao)}, Código de exceção: {hex(codigo_excecao)}")
                return []

            byte_count = response[8]
            coil_data = response[9:9 + byte_count]

            # Converter os dados dos coils em estados booleanos
            coil_states = []
            for byte in coil_data:
                for bit in range(8):
                    coil_states.append(bool(byte & (1 << bit)))
                    if len(coil_states) == quantity:
                        break

            print(f"Estados dos coils: {coil_states}")
            return coil_states

        except Exception as e:
            print(f"Erro ao ler o coil: {e}")
            return []

    def close_socket(self):
        self.socket.close()
