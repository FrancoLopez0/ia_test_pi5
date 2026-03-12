from fastapi import FastAPI
from pydantic import BaseModel
from ollama import AsyncClient
import time

app = FastAPI()
client = AsyncClient() # Reutilizar la instancia del cliente es clave

class CommandRequest(BaseModel):
    prompt: str

# Diccionario local en memoria (Cero latencia, fácil de actualizar)
WAYPOINTS = {
    "W_DOOR": "X28Y50",
    "W_HOME": "X0Y0",
    "W_LOAD": "X10Y10",
}

def parse_llm_output(raw_output: str):
    cmd = raw_output.strip().upper()
    
    # Si es un waypoint (empieza con W_)
    if cmd.startswith("W_"):
        coordenada = WAYPOINTS.get(cmd, "X0Y0") # Por defecto vuelve a la base si alucina
        return coordenada
        
    # Si es un comando de movimiento (R80, S0, etc)
    return cmd

@app.post("/execute")
async def execute_command(req: CommandRequest):
    t0 = time.time()
    
    # API Generate cruda, sin tokens de chat
    response = await client.generate(
        model='custom-llm-0.5b',
        prompt=f"INPUT: {req.prompt}\nOUTPUT:",
        options={'num_predict': 5, 'temperature': 0.0}
    )
    
    # Parseo de tu DSL (ej: R80)
    raw_cmd = response['response'].strip()

    cmd = parse_llm_output(raw_cmd)
    
    return {
        "command": cmd,
        "processing_time_ms": round((time.time() - t0) * 1000, 2)
    }