import os
import json
import difflib
import requests
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass
try:
    import openai  # legacy <1.0.0 or new >=1.0.0 root module
    OPENAI_VERSION = getattr(openai, "__version__", "")
except Exception:
    openai = None
    OPENAI_VERSION = ""
try:
    from openai import OpenAI  # new client class in >=1.0.0
except Exception:
    OpenAI = None


def _safe_json_parse(text: str):
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except Exception:
            pass
    return None
def _ascii_clean(s: str) -> str:
    try:
        return s.encode("ascii", "ignore").decode("ascii")
    except Exception:
        return s


def _normalize_model(name: str | None) -> str | None:
    if not name:
        return name
    n = name.strip()
    aliases = {
        "gpt-4-mini": "gpt-4o-mini",
        "gpt4-mini": "gpt-4o-mini",
        "gpt-4o-mini-vision": "gpt-4o-mini",  # prefer unified model
        "gpt-4.1mini": "gpt-4.1-mini",
    }
    return aliases.get(n, n)


def _responses_http_call(api_key: str, model: str, prompt_text: str, b64_image: str, include_schema: bool = True) -> str:
    url = "https://api.openai.com/v1/responses"
    # Build response_format schema (structured output)
    output_lang = os.getenv("OUTPUT_LANG", "en").lower()
    properties = {
        "label": {"type": "string"},
        "confidence": {"type": "number"},
        "calories_kcal": {"type": "number"},
        "serving": {"type": "string"},
        "notes": {"type": "string"},
    }
    required = ["label", "confidence", "calories_kcal", "serving", "notes"]
    if output_lang == "ko":
        properties.update({
            "label_ko": {"type": "string"},
            "serving_ko": {"type": "string"},
            "notes_ko": {"type": "string"},
        })
        required += ["label_ko", "serving_ko", "notes_ko"]
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "food_result",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": properties,
                "required": required,
            },
            "strict": True,
        },
    }
    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt_text},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_image}"},
                ],
            }
        ],
        "max_output_tokens": 500,
        "temperature": 0,
    }
    if include_schema:
        payload["response_format"] = response_format
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "food-classifier/1.0",
    }
    s = requests.Session()
    s.trust_env = False  # ignore proxy/env that may inject non-ascii headers
    data_bytes = json.dumps(payload, ensure_ascii=True).encode("ascii")
    r = s.post(url, headers=headers, data=data_bytes, timeout=90)
    if r.status_code == 400 and include_schema:
        # Fallback without schema if server rejects response_format
        return _responses_http_call(api_key, model, prompt_text, b64_image, include_schema=False)
    r.raise_for_status()
    data = r.json()
    # Prefer aggregated output_text if present
    text = data.get("output_text")
    if text:
        return text
    # Reconstruct from output structure
    out = data.get("output", [])
    return "".join([p.get("text", "") for o in out for p in o.get("content", [])])


def _chat_completions_http_call(api_key: str, model: str, prompt_text: str, b64_image: str, include_json_object: bool = True) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    # Ask for a JSON object; schema enforcement not supported here
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                ],
            }
        ],
        "max_tokens": 500,
        "temperature": 0,
    }
    if include_json_object:
        payload["response_format"] = {"type": "json_object"}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "food-classifier/1.0",
    }
    s = requests.Session()
    s.trust_env = False
    data_bytes = json.dumps(payload, ensure_ascii=True).encode("ascii")
    r = s.post(url, headers=headers, data=data_bytes, timeout=90)
    if r.status_code == 400 and include_json_object:
        # Retry without response_format (older API)
        return _chat_completions_http_call(api_key, model, prompt_text, b64_image, include_json_object=False)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def classify_image_base64(b64_image: str, prompt_override: str | None = None):
    api_key = os.getenv("OPENAI_API_KEY")
    requested_model = _normalize_model(os.getenv("CHAT_MODEL", "gpt-4o-mini"))
    output_lang = os.getenv("OUTPUT_LANG", "en").lower()

    # Load allowed labels list if present for constrained classification
    labels_path = os.path.join(os.path.dirname(__file__), "food_labels.json")
    allowed_labels = []
    if os.path.exists(labels_path):
        try:
            with open(labels_path, "r", encoding="utf-8") as f:
                allowed_labels = json.load(f)
        except Exception:
            allowed_labels = []

    # Ensure ASCII-only labels for tricky environments
    allowed_labels_ascii = [_ascii_clean(str(x)) for x in allowed_labels]
    label_block = "\nAllowed labels: " + ", ".join(allowed_labels_ascii) if allowed_labels_ascii else ""

    # ASCII-only prompt (English) to avoid any encoding issues on some environments.
    schema_base = (
        "{\n  \"label\": string,\n  \"confidence\": number,\n  \"calories_kcal\": number,\n  \"serving\": string,\n  \"notes\": string\n}\n"
    )
    ko_instruction = (
        "Additionally, include 'label_ko', 'serving_ko', and 'notes_ko' with Korean strings. "
        "'label' must still be from the English allowed list, but 'label_ko' is the Korean name.\n"
        if output_lang == "ko" else ""
    )
    prompt = prompt_override or (
        "Look at the image and return the best-matching food label (use one from the allowed list or 'unknown') and an average calorie estimate.\n"
        "Respond with JSON only, no extra text. JSON schema (base):\n"
        + schema_base +
        ("Output language: Korean fields requested. " + ko_instruction if output_lang == "ko" else "") +
        "Rules:\n- label must be from the allowed list or 'unknown'\n- confidence is 0..1\n- calories_kcal is a single representative value (put ranges in notes)\n- notes should include uncertainty or 2-3 alternatives if relevant\n"
        + label_block + "\n"
        "Be conservative on calories; if not confident in the label, use 'unknown' and list alternatives in notes."
    )

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일 또는 PowerShell 환경변수를 설정하세요.")
    if api_key in {"YOUR_KEY", "PASTE_API_KEY"} or api_key.lower().startswith("sk-" ) is False:
        raise RuntimeError("유효하지 않은 API 키 형식 입니다. 실제 OpenAI 키(sk-로 시작)를 .env 또는 환경변수로 설정하세요.")
    # Validate API key is ASCII for HTTP header safety
    try:
        ("Bearer " + api_key).encode("latin-1")
    except Exception:
        raise RuntimeError("OPENAI_API_KEY 값에 비-ASCII 문자가 포함되어 있습니다. 메모장에 붙여넣어 공백/스마트따옴표를 제거하고 다시 복사해 주세요.")

    if not (OpenAI or openai):
        raise RuntimeError("openai 패키지가 설치되지 않았습니다. 'pip install openai' 후 다시 시도하세요.")

    # Decide which path to use. Prefer new SDK if available OR if model name implies vision.
    force_new = requested_model.endswith("-vision") or requested_model.startswith("gpt-4o") or requested_model.startswith("gpt-4.1")
    use_new = OpenAI is not None and force_new

    # If user requested a *-vision model but new SDK not available, fail fast with guidance.
    if requested_model.endswith("-vision") and OpenAI is None:
        raise RuntimeError(
            "요청한 모델 '" + requested_model + "' 은 deprecated preview 또는 신규 통합 비전 모델입니다. openai 패키지를 업그레이드 하세요:\n"
            "  python -m pip install --upgrade openai\n" 
            "업그레이드 후 CHAT_MODEL을 'gpt-4o-mini' 또는 'gpt-4.1-mini' 처럼 -vision 없이 설정해 주세요."
        )

    # Legacy model name mapping (kept only for backward compatibility; deprecated vision preview will soon retire).
    legacy_alias = {
        "gpt-4o-mini-vision": "gpt-4-vision-preview",  # will deprecate
        "gpt-4.1-mini-vision": "gpt-4-vision-preview",  # will deprecate
    }

    if use_new:
        try:
            client = OpenAI(api_key=api_key)
            # Build structured output schema (for newer SDKs)
            properties = {
                "label": {"type": "string"},
                "confidence": {"type": "number"},
                "calories_kcal": {"type": "number"},
                "serving": {"type": "string"},
                "notes": {"type": "string"},
            }
            required = ["label", "confidence", "calories_kcal", "serving", "notes"]
            if output_lang == "ko":
                properties.update({
                    "label_ko": {"type": "string"},
                    "serving_ko": {"type": "string"},
                    "notes_ko": {"type": "string"},
                })
                required += ["label_ko", "serving_ko", "notes_ko"]
            try:
                response = client.responses.create(
                    model=requested_model,
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_image}"},
                            ],
                        }
                    ],
                    max_output_tokens=500,
                    temperature=0,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "food_result",
                            "schema": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": properties,
                                "required": required,
                            },
                            "strict": True,
                        },
                    },
                )
            except TypeError as te:
                # Older SDK without response_format kw; retry without it
                response = client.responses.create(
                    model=requested_model,
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_image}"},
                            ],
                        }
                    ],
                    max_output_tokens=500,
                    temperature=0,
                )
            text = getattr(response, "output_text", "") or "".join(
                [p.get("text", "") for o in getattr(response, "output", []) for p in o.get("content", [])]
            )
        except Exception as e:
            # Fallback to Chat Completions if encoding error occurs
            if "ascii" in str(e).lower() or "encode" in str(e).lower():
                try:
                    try:
                        chat = client.chat.completions.create(
                            model=requested_model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                                        },
                                    ],
                                }
                            ],
                            max_tokens=500,
                            temperature=0,
                            response_format={"type": "json_object"},
                        )
                    except TypeError:
                        # Older SDK without response_format
                        chat = client.chat.completions.create(
                            model=requested_model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                                        },
                                    ],
                                }
                            ],
                            max_tokens=500,
                            temperature=0,
                        )
                    text = chat.choices[0].message.content
                except Exception as ee:
                    # Last resort: sanitize prompt to pure ASCII and retry Responses once
                    try:
                        prompt2 = _ascii_clean(prompt)
                        # Try raw HTTP to responses endpoint (utf-8)
                        try:
                            text = _responses_http_call(api_key, requested_model, prompt2, b64_image, include_schema=True)
                        except Exception:
                            text = _responses_http_call(api_key, requested_model, prompt2, b64_image, include_schema=False)
                    except Exception as e3:
                        # Try raw HTTP to chat completions as final attempt
                        try:
                            try:
                                text = _chat_completions_http_call(api_key, requested_model, prompt2, b64_image, include_json_object=True)
                            except Exception:
                                text = _chat_completions_http_call(api_key, requested_model, prompt2, b64_image, include_json_object=False)
                        except Exception as e4:
                            raise RuntimeError(f"OpenAI new API call failed (fallback also failed): {e4}")
            else:
                # If failure is due to response_format kw on older SDK, try raw HTTP path
                if isinstance(e, TypeError) and "response_format" in str(e):
                    try:
                        text = _responses_http_call(api_key, requested_model, prompt, b64_image, include_schema=True)
                    except Exception:
                        text = _responses_http_call(api_key, requested_model, prompt, b64_image, include_schema=False)
                else:
                    raise RuntimeError(f"OpenAI new API call failed: {e}")
    else:
        if not (openai and hasattr(openai, "ChatCompletion")):
            raise RuntimeError(
                "레거시 ChatCompletion 경로를 사용할 수 없습니다. openai 패키지를 업그레이드 해서 새 SDK를 사용하세요: pip install --upgrade openai"
            )
        openai.api_key = api_key
        legacy_model = legacy_alias.get(requested_model, requested_model)
        if legacy_model == "gpt-4-vision-preview":
            raise RuntimeError(
                "'gpt-4-vision-preview' 는 더 이상 지원되지 않습니다. openai>=1.0.0 업그레이드 후 CHAT_MODEL='gpt-4o-mini' 로 설정하세요."
            )
        try:
            resp = openai.ChatCompletion.create(
                model=legacy_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.0,
            )
            text = resp["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenAI legacy call failed: {e}. SDK 버전 확인 및 'pip install --upgrade openai' 수행 후 vision 전용 모델 사용을 권장합니다.")

    parsed = _safe_json_parse(text)
    if parsed is None:
        return {"raw": text}

    # If label not in allowed list and list exists, attempt fuzzy correction
    if allowed_labels and isinstance(parsed, dict):
        label = str(parsed.get("label", "")).lower().strip()
        if label and label not in [l.lower() for l in allowed_labels] and label != "unknown":
            # Fuzzy match
            candidates = difflib.get_close_matches(label, allowed_labels, n=1, cutoff=0.6)
            if candidates:
                parsed["label_original"] = label
                parsed["label"] = candidates[0]
                note_extra = f"자동 교정: '{label}' -> '{candidates[0]}' (fuzzy)"
                notes = parsed.get("notes", "")
                parsed["notes"] = (notes + ("; " if notes else "") + note_extra)[:400]
            else:
                # Insert unknown fallback if no reasonable match
                parsed["label_original"] = label
                parsed["label"] = "unknown"
                notes = parsed.get("notes", "")
                parsed["notes"] = (notes + ("; " if notes else "") + "허용 목록과 불일치하여 unknown 처리")[:400]
    return parsed


def classify_image_base64_reasoned(b64_image: str, primary_model_env: str = "CHAT_MODEL", fallback_model_env: str = "CHAT_MODEL_FALLBACK"):
    """Two-pass reasoning + fallback model path.
    1) First pass: lightweight model generates candidate labels (not JSON) constrained by list.
    2) Second pass: larger model (or same if fallback absent) produces final JSON.
    If second model missing, degrade to single pass classify_image_base64.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

    labels_path = os.path.join(os.path.dirname(__file__), "food_labels.json")
    allowed_labels = []
    if os.path.exists(labels_path):
        try:
            with open(labels_path, "r", encoding="utf-8") as f:
                allowed_labels = json.load(f)
        except Exception:
            allowed_labels = []

    primary = _normalize_model(os.getenv(primary_model_env, os.getenv("CHAT_MODEL", "gpt-4o-mini")))
    fallback = _normalize_model(os.getenv(fallback_model_env, "gpt-4.1-mini"))
    if primary == fallback:
        fallback = None  # avoid duplicate call
    output_lang = os.getenv("OUTPUT_LANG", "en").lower()

    # Lightweight first reasoning prompt
    reasoning_prompt = (
        "List up to 4 food label candidates from the image with a short reason for each. Exclude labels not in the allowed list. "
        "Output format: 'label1 | reason; label2 | reason; ...'"
        + (" Allowed list: " + ", ".join(allowed_labels) if allowed_labels else "")
    )

    def _call_model(model_name: str, text_prompt: str, image_b64: str):
        os.environ["CHAT_MODEL"] = model_name  # reuse underlying function path
        # Reuse low-level path with simplified JSON-free prompt when reasoning phase
        api_key_inner = os.getenv("OPENAI_API_KEY")
        if not (OpenAI or openai):
            raise RuntimeError("openai 패키지 필요")
        force_new = model_name.startswith("gpt-4o") or model_name.startswith("gpt-4.1")
        use_new = OpenAI is not None and force_new
        if use_new:
            client = OpenAI(api_key=api_key_inner)
            resp = client.responses.create(
                model=model_name,
                input=[{"role": "user", "content": [
                    {"type": "input_text", "text": text_prompt},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_b64}"},
                ]}],
                max_output_tokens=400,
                temperature=0,
            )
            return getattr(resp, "output_text", "") or "".join([
                p.get("text", "") for o in getattr(resp, "output", []) for p in o.get("content", [])
            ])
        else:
            if not (openai and hasattr(openai, "ChatCompletion")):
                raise RuntimeError("레거시 ChatCompletion 사용 불가. openai 업그레이드 필요.")
            openai.api_key = api_key_inner
            r = openai.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "user", "content": text_prompt}],
                max_tokens=400,
                temperature=0,
            )
            return r["choices"][0]["message"]["content"]

    try:
        reasoning_text = _call_model(primary, reasoning_prompt, b64_image)
    except Exception:
        # fallback directly to single-pass
        return classify_image_base64(b64_image)

    # Extract candidate labels
    candidates_raw = [seg.strip() for seg in reasoning_text.split(";") if seg.strip()]
    candidates = []
    for item in candidates_raw:
        label_part = item.split("|")[0].strip().lower()
        if allowed_labels:
            if label_part in [l.lower() for l in allowed_labels]:
                candidates.append(label_part)
        else:
            candidates.append(label_part)
    candidates = candidates[:4]
    candidate_block = ", ".join(candidates)

    ko_addendum = (
        "Also include 'label_ko', 'serving_ko', and 'notes_ko' in Korean. 'label' remains from the English allowed list."
        if output_lang == "ko" else ""
    )
    final_prompt = (
        "Choose the single best label from the candidates for the image, or use 'unknown' if not confident. Respond ONLY with JSON.\n"
        "Candidates: " + (candidate_block if candidate_block else "(none)") + "\n"
        "Follow the same JSON schema {label, confidence, calories_kcal, serving, notes}. Put alternatives/uncertainty in notes. "
        + ko_addendum
    )

    # Use fallback (larger) model if available
    target_model = fallback or primary
    os.environ["CHAT_MODEL"] = target_model
    final_result = classify_image_base64(b64_image, prompt_override=final_prompt)
    # Attach reasoning trace if dict
    if isinstance(final_result, dict):
        final_result["reasoning_trace"] = {
            "primary_model": primary,
            "fallback_model": target_model,
            "raw_reasoning": reasoning_text,
            "candidates": candidates,
        }
    return final_result
