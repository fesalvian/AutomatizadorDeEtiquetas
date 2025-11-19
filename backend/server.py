# backend/server.py
import asyncio
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from openai import OpenAI
import os
import base64
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

next_id = 0
labels = []

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# 1) Receber etiqueta manual
# ---------------------------------------------------
@app.post("/add-label")
async def add_label(data: dict):
    global next_id
    data["id"] = next_id
    next_id += 1
    labels.append(data)
    return {"status": "ok"}


# ---------------------------------------------------
# 2) Deletar
# ---------------------------------------------------
@app.delete("/delete/{item_id}")
async def delete_label(item_id: int):
    global labels
    for i, item in enumerate(labels):
        if item["id"] == item_id:
            labels.pop(i)
            return {"status": "ok"}
    return {"status": "error", "message": "ID não encontrado"}


@app.delete("/clear")
async def clear_labels():
    labels.clear()
    return {"status": "ok"}


# ---------------------------------------------------
# 3) OCR com IA
# ---------------------------------------------------
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    global next_id

    img_bytes = await file.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    print("Imagem recebida para OCR.")

    prompt = """
        Extraia todas as etiquetas da imagem e retorne SOMENTE um JSON.
        Formato EXATO:

        [
          {
            "comodo": "Banheiro",
            "peca": "Porta toalha",
            "medida1": "0300",
            "medida2": "0500",
            "quantidade": 2
          }
        ]

        Se faltar algo, chute o mais provável.
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{file.content_type};base64,{img_b64}"
                    }
                ]
            }
        ]
    )

    text = response.output_text
    print("RAW IA:", text)

    try:
        start = text.index("[")
        end = text.rindex("]") + 1
        etiquetas = json.loads(text[start:end])
    except Exception as e:
        print("Erro ao parsear JSON:", e)
        return {"status": "error", "message": "JSON inválido da IA"}

    print("Etiquetas detectadas:", etiquetas)

    # adicionar ao sistema
    for item in etiquetas:
        item["id"] = next_id
        next_id += 1
        labels.append(item)

    return {
        "status": "ok",
        "total_detectado": len(etiquetas),
        "etiquetas": etiquetas
    }

# ---------------------------------------------------
# EDITAR
# ---------------------------------------------------
@app.put("/edit/{item_id}")
async def edit_label(item_id: int, data: dict):
    for i, item in enumerate(labels):
        if item["id"] == item_id:
            data["id"] = item_id
            labels[i] = data
            return {"status": "ok"}

    return {"status": "error", "message": "ID não encontrado"}


# ---------------------------------------------------
# GET LISTA
# ---------------------------------------------------
@app.get("/labels")
async def get_labels():
    return labels


# ---------------------------------------------------
# WEBSOCKET FUTURO
# ---------------------------------------------------
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    print("WS conectado")
    try:
        while True:
            msg = await ws.receive_text()
            print("WS recebeu:", msg)
    except:
        print("WS caiu")


def start_server():
    print("FastAPI rodando http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="critical", access_log=False)


if __name__ == "__main__":
    start_server()
