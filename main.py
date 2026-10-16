from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn

# Importamos la base de datos y nuestra lógica
from database import SessionLocal, HistorialTuring
from maquina_turing import MaquinaTuringDPI

app = FastAPI(title="Validador DPI - Máquina de Turing", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite peticiones desde cualquier origen (tu HTML local)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para inyectar la sesión de base de datos en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo de Pydantic (Lo que el usuario nos envía)
class TuringRequest(BaseModel):
    numero_nodos: int
    alfabeto: str
    cadena_analizar: str
    metodo_solucion: str

@app.post("/analizar_dpi")
def analizar_dpi(request: TuringRequest, db: Session = Depends(get_db)):
    # 1. Ejecutar el análisis con nuestra Máquina de Turing
    try:
        maquina = MaquinaTuringDPI(request.cadena_analizar, metodo=request.metodo_solucion)
        resultado = maquina.procesar()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la máquina: {str(e)}")

    # 2. Guardar el registro en PostgreSQL
    nuevo_registro = HistorialTuring(
        cadena_entrada=request.cadena_analizar,
        alfabeto=request.alfabeto,
        nodos_configurados=request.numero_nodos,
        metodo=request.metodo_solucion,
        cinta_resultante=resultado["cinta_resultante"],
        estado_final=resultado["estado_final"],
        log_transiciones=resultado["transiciones"]
    )
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro) # Refresca para obtener el 'id' generado por la BD

    # 3. Devolver la respuesta completa
    return {
        "id_db": nuevo_registro.id,
        "cadena_original": request.cadena_analizar,
        "metodo_aplicado": request.metodo_solucion,
        "resultado_final": resultado["estado_final"],
        "cinta_resultante": resultado["cinta_resultante"],
        "historial_transiciones": resultado["transiciones"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)