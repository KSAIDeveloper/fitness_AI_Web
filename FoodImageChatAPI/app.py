import os
import base64
import json
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import chat_client

app = FastAPI()

# Allow SPA (Vite dev server) to call this API from browser
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

@app.get('/health')
async def health():
    return {"status": "ok"}


@app.get('/', response_class=HTMLResponse)
async def homepage():
    html = """<!doctype html>
    <html><head><meta charset='utf-8'><title>Food Classifier</title></head>
    <body>
      <h1>Food Image Classifier (Chat API prototype)</h1>
      <form action="/classify" enctype="multipart/form-data" method="post">
        <input name="image" type="file" accept="image/*" required />
        <label for="mode">Mode:</label>
        <select name="mode">
          <option value="chat">Chat API (default)</option>
          <option value="local">Local model (fallback)</option>
        </select>
        <button type="submit">Classify</button>
      </form>
      <p>See README for setup and API key instructions.</p>
    </body></html>"""
    return HTMLResponse(content=html)


@app.post('/classify')
async def classify(image: UploadFile = File(...), mode: str = Form(None)):
    content = await image.read()
    b64 = base64.b64encode(content).decode('utf-8')
    chosen_mode = (mode or os.getenv('MODE', 'chat')).lower()
    if chosen_mode == 'local':
        try:
            # import the fixed local model implementation
            from local_model_fixed import local_inference

            res = local_inference(content)
            return JSONResponse(res)
        except Exception as e:
            return JSONResponse({"error": "local model not available", "detail": str(e)}, status_code=500)

    try:
        # Two-pass reasoning fallback if enabled via env USE_REASONING=1
        use_reasoning = os.getenv("USE_REASONING", "0") == "1"
        if use_reasoning:
            result = chat_client.classify_image_base64_reasoned(b64)
        else:
            result = chat_client.classify_image_base64(b64)

        # If the client returned a raw string, try to parse JSON out of it
        parsed = None
        if isinstance(result, str):
            try:
                parsed = json.loads(result)
            except Exception:
                # try to extract JSON block
                from chat_client import _safe_json_parse

                parsed = _safe_json_parse(result)
        elif isinstance(result, dict):
            parsed = result

        if not parsed:
            # couldn't parse JSON, return raw
            return JSONResponse({"raw": result})

        # Format a human-friendly Korean text response (prefer *_ko fields if present)
        label = parsed.get("label_ko") or parsed.get("label", "알 수 없음")
        confidence = parsed.get("confidence")
        calories = parsed.get("calories_kcal")
        serving = parsed.get("serving_ko") or parsed.get("serving", "-")
        notes = parsed.get("notes_ko") or parsed.get("notes", "")

        conf_text = ""
        try:
            if confidence is not None:
                conf_text = f" (신뢰도: {float(confidence):.2f})"
        except Exception:
            conf_text = ""

        calories_text = "알 수 없음"
        try:
            if calories is not None:
                # show integer if close to integer
                if abs(float(calories) - int(float(calories))) < 0.5:
                    calories_text = f"{int(round(float(calories)))} kcal"
                else:
                    calories_text = f"{round(float(calories),1)} kcal"
        except Exception:
            calories_text = "알 수 없음"

        text = (
            f"음식 이름 : {label}{conf_text}\n"
            f"칼로리 (평균) : {calories_text}\n"
            f"1회 제공량 : {serving}\n"
            f"메모 : {notes}"
        )

        return JSONResponse({"text": text, "data": parsed})
    except Exception as e:
        return JSONResponse({"error": "chat classify failed", "detail": str(e)}, status_code=500)
