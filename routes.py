from fastapi import FastAPI, HTTPException
from driver import Driver
import time
driver = Driver('192.168.15.1', 502, 1)
app = FastAPI()

@app.get('/led/{id_led}')
def turn_led(id_led: int):
    if id_led < 0:
        raise HTTPException(status_code=400, detail="Parâmetro 'id_led' não pode ser menor que 0")
    driver.send_action_button(id_led, True)
    time.sleep(10)
    driver.send_action_button(id_led, False)
    
