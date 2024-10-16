from fastapi import FastAPI, HTTPException
from driver import Driver
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuração do middleware CORS para permitir qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permitir qualquer método (GET, POST, etc.)
    allow_headers=["*"],  # Permitir qualquer cabeçalho
)

@app.get('/led/{id_led}')
async def turn_led(id_led: int):
    if id_led < 0:
        raise HTTPException(status_code=400, detail="Parâmetro 'id_led' não pode ser menor que 0")
    
    try:
        driver = Driver('192.168.15.1', 502, 1)  # Nova instância para cada request
        print(f"Ligando LED {id_led}")
        driver.send_action_button(id_led, True)
        
        await asyncio.sleep(3)  # Função assíncrona não bloqueante
        
        print(f"Desligando LED {id_led}")
        driver.send_action_button(id_led, False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao controlar o LED: {str(e)}")

    finally:
        driver.close_socket()  # Certifique-se de fechar a conexão
