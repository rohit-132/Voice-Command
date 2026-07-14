import os
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# We'll use google-genai as recommended by the deprecation warning, or fallback to generativeai
try:
    from google import genai
    from google.genai import types
    USE_NEW_SDK = True
except ImportError:
    import google.generativeai as genai_old
    USE_NEW_SDK = False

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class CommandRequest(BaseModel):
    transcript: str
    language: str = "en-US"

class ProcessedCommand(BaseModel):
    intent: str
    item: str | None = None
    quantity: int = 1
    category: str = "other"
    maxPrice: float | None = None
    message: str | None = None

SYSTEM_PROMPT = """
You are a Natural Language Processing engine for a Shopping Assistant app.
Analyze the user's voice transcript and extract the intent and parameters.
Ensure the extracted item is translated into English for standardisation.
Generate a friendly success/response message in the user's original language based on the user's Language Code.
The output MUST be a valid JSON object matching this schema exactly:
{
  "intent": "ADD" | "REMOVE" | "SEARCH" | "UPDATE" | "CLEAR" | "CHECK" | "UNKNOWN",
  "item": "string (the clean item name in English, without numbers, quantities, or units like '10' or 'bottle of')",
  "quantity": integer (extract the number if present, default 1),
  "category": "produce" | "dairy" | "bakery" | "meat" | "pantry" | "snacks" | "beverages" | "other",
  "maxPrice": float or null (if intent is SEARCH and they specified a price limit),
  "message": "string (localized response message for the user in the language specified by the Language Code)"
}
Return ONLY the raw JSON string. Do not wrap in markdown block quotes. Do not include any explanations.

Examples:
Language Code: en-US
Transcript: "Can you add a couple of organic apples to my list?"
Output: {"intent": "ADD", "item": "organic apples", "quantity": 2, "category": "produce", "maxPrice": null, "message": "Added 2 organic apples to your list."}

Language Code: es-ES
Transcript: "Elimina la leche, por favor."
Output: {"intent": "REMOVE", "item": "milk", "quantity": 1, "category": "dairy", "maxPrice": null, "message": "He eliminado la leche de tu lista."}
"""


def get_language_family(language: str) -> str:
    lang = (language or "en-US").split("-")[0].lower()
    return {
        "en": "en",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "pt": "pt",
        "nl": "nl",
        "ar": "ar",
        "hi": "hi",
        "ja": "ja",
        "ko": "ko",
        "zh": "zh"
    }.get(lang, "en")


def build_localized_message(intent: str, item: str, quantity: int, language: str) -> str:
    lang_family = get_language_family(language)
    item_text = item.strip() or "item"

    if lang_family == "es":
        if intent == "ADD":
            return f"Añadido {quantity} {item_text}."
        if intent == "REMOVE":
            return f"Se ha eliminado {item_text}."
        if intent == "SEARCH":
            return f"Buscando {item_text}..."
        if intent == "UPDATE":
            return f"Actualizado {item_text} a {quantity}."
        if intent == "CLEAR":
            return "Lista vaciada."
        if intent == "CHECK":
            return f"Comprobando {item_text}..."
    elif lang_family == "fr":
        if intent == "ADD":
            return f"Ajouté {quantity} {item_text}."
        if intent == "REMOVE":
            return f"{item_text} retiré."
        if intent == "SEARCH":
            return f"Recherche de {item_text}..."
        if intent == "UPDATE":
            return f"Mis à jour {item_text} à {quantity}."
        if intent == "CLEAR":
            return "Liste vidée."
        if intent == "CHECK":
            return f"Vérification de {item_text}..."
    elif lang_family == "de":
        if intent == "ADD":
            return f"{quantity} {item_text} hinzugefügt."
        if intent == "REMOVE":
            return f"{item_text} entfernt."
        if intent == "SEARCH":
            return f"Suche nach {item_text}..."
        if intent == "UPDATE":
            return f"{item_text} auf {quantity} aktualisiert."
        if intent == "CLEAR":
            return "Liste geleert."
        if intent == "CHECK":
            return f"Prüfe {item_text}..."
    elif lang_family == "it":
        if intent == "ADD":
            return f"Aggiunto {quantity} {item_text}."
        if intent == "REMOVE":
            return f"{item_text} rimosso."
        if intent == "SEARCH":
            return f"Sto cercando {item_text}..."
        if intent == "UPDATE":
            return f"Aggiornato {item_text} a {quantity}."
        if intent == "CLEAR":
            return "Lista cancellata."
        if intent == "CHECK":
            return f"Controllo {item_text}..."
    elif lang_family == "pt":
        if intent == "ADD":
            return f"Adicionado {quantity} {item_text}."
        if intent == "REMOVE":
            return f"{item_text} removido."
        if intent == "SEARCH":
            return f"Procurando {item_text}..."
        if intent == "UPDATE":
            return f"Atualizado {item_text} para {quantity}."
        if intent == "CLEAR":
            return "Lista limpa."
        if intent == "CHECK":
            return f"Verificando {item_text}..."
    elif lang_family == "nl":
        if intent == "ADD":
            return f"{quantity} {item_text} toegevoegd."
        if intent == "REMOVE":
            return f"{item_text} verwijderd."
        if intent == "SEARCH":
            return f"Zoeken naar {item_text}..."
        if intent == "UPDATE":
            return f"{item_text} bijgewerkt naar {quantity}."
        if intent == "CLEAR":
            return "Lijst geleegd."
        if intent == "CHECK":
            return f"Controleren {item_text}..."
    elif lang_family == "ar":
        if intent == "ADD":
            return f"تمت إضافة {quantity} {item_text}."
        if intent == "REMOVE":
            return f"تمت إزالة {item_text}."
        if intent == "SEARCH":
            return f"جارٍ البحث عن {item_text}..."
        if intent == "UPDATE":
            return f"تم تحديث {item_text} إلى {quantity}."
        if intent == "CLEAR":
            return "تمت очист القائمة."
        if intent == "CHECK":
            return f"جارٍ التحقق من {item_text}..."
    elif lang_family == "hi":
        if intent == "ADD":
            return f"{quantity} {item_text} जोड़ा गया।"
        if intent == "REMOVE":
            return f"{item_text} हटा दिया गया।"
        if intent == "SEARCH":
            return f"{item_text} खोजा जा रहा है..."
        if intent == "UPDATE":
            return f"{item_text} को {quantity} पर अपडेट किया गया।"
        if intent == "CLEAR":
            return "सूची साफ़ कर दी गई।"
        if intent == "CHECK":
            return f"{item_text} की जाँच की जा रही है..."
    elif lang_family == "ja":
        if intent == "ADD":
            return f"{quantity} 個の {item_text} を追加しました。"
        if intent == "REMOVE":
            return f"{item_text} を削除しました。"
        if intent == "SEARCH":
            return f"{item_text} を検索しています..."
        if intent == "UPDATE":
            return f"{item_text} を {quantity} に更新しました。"
        if intent == "CLEAR":
            return "リストをクリアしました。"
        if intent == "CHECK":
            return f"{item_text} を確認しています..."
    elif lang_family == "ko":
        if intent == "ADD":
            return f"{quantity}개의 {item_text}를 추가했습니다."
        if intent == "REMOVE":
            return f"{item_text}를 제거했습니다."
        if intent == "SEARCH":
            return f"{item_text}를 검색하는 중..."
        if intent == "UPDATE":
            return f"{item_text}를 {quantity}개로 업데이트했습니다."
        if intent == "CLEAR":
            return "목록을 비웠습니다."
        if intent == "CHECK":
            return f"{item_text}를 확인하는 중..."
    elif lang_family == "zh":
        if intent == "ADD":
            return f"已添加 {quantity} 个 {item_text}。"
        if intent == "REMOVE":
            return f"已移除 {item_text}。"
        if intent == "SEARCH":
            return f"正在搜索 {item_text}..."
        if intent == "UPDATE":
            return f"已将 {item_text} 更新为 {quantity}。"
        if intent == "CLEAR":
            return "列表已清空。"
        if intent == "CHECK":
            return f"正在检查 {item_text}..."

    if intent == "ADD":
        return f"Added {quantity} {item_text} to your list."
    if intent == "REMOVE":
        return f"Removed {item_text} from your list."
    if intent == "SEARCH":
        return f"Searching for {item_text}..."
    if intent == "UPDATE":
        return f"Updated {item_text} to {quantity}."
    if intent == "CLEAR":
        return "List cleared."
    if intent == "CHECK":
        return f"Checking for {item_text}..."
    return "I'm not sure how to handle that."


def fallback_parser(transcript: str, language: str = "en-US") -> dict:
    """A basic rule-based parser that kicks in if the Gemini API key is invalid or missing."""
    text = transcript.lower().strip()
    intent = "UNKNOWN"
    item = ""
    quantity = 1
    maxPrice = None
    language_family = get_language_family(language)

    keyword_groups = {
        "en": {
            "search": ['find', 'search', 'looking'],
            "remove": ['remove', 'delete', 'take off'],
            "update": ['update', 'change'],
            "clear": ['clear', 'empty'],
            "check": ['check', 'do i have'],
            "add": ['add', 'buy', 'i need']
        },
        "es": {
            "search": ['buscar', 'encuentra', 'buscar'],
            "remove": ['eliminar', 'quitar', 'borrar'],
            "update": ['actualizar', 'cambiar'],
            "clear": ['vaciar', 'limpiar'],
            "check": ['comprobar', 'tengo'],
            "add": ['añadir', 'comprar', 'necesito']
        },
        "fr": {
            "search": ['trouver', 'chercher', 'recherche'],
            "remove": ['supprimer', 'enlever'],
            "update": ['modifier', 'changer'],
            "clear": ['vider', 'effacer'],
            "check": ['vérifier', 'est-ce que j\'ai'],
            "add": ['ajouter', 'acheter', 'j\'ai besoin']
        },
        "de": {
            "search": ['suche', 'finden', 'suchen'],
            "remove": ['entfernen', 'löschen'],
            "update": ['aktualisieren', 'ändern'],
            "clear": ['leeren', 'löschen'],
            "check": ['prüfen', 'habe ich'],
            "add": ['hinzufügen', 'kaufen', 'brauche']
        },
        "it": {
            "search": ['cerca', 'trova', 'cercare'],
            "remove": ['rimuovi', 'elimina', 'togli'],
            "update": ['aggiorna', 'cambia'],
            "clear": ['svuota', 'pulisci'],
            "check": ['controlla', 'ho'],
            "add": ['aggiungi', 'comprare', 'ho bisogno']
        },
        "pt": {
            "search": ['procurar', 'buscar', 'encontrar'],
            "remove": ['remover', 'apagar', 'tirar'],
            "update": ['atualizar', 'mudar'],
            "clear": ['limpar', 'esvaziar'],
            "check": ['verificar', 'tenho'],
            "add": ['adicionar', 'comprar', 'preciso']
        },
        "nl": {
            "search": ['zoek', 'vinden', 'zoeken'],
            "remove": ['verwijder', 'haal weg'],
            "update": ['update', 'wijzig'],
            "clear": ['wissen', 'leegmaken'],
            "check": ['controleer', 'heb ik'],
            "add": ['voeg toe', 'koop', 'ik heb nodig']
        },
        "ar": {
            "search": ['ابحث', 'بحث', 'اعثر'],
            "remove": ['أزل', 'احذف', 'إزالة'],
            "update": ['حدث', 'غيّر'],
            "clear": ['امسح', 'أفرغ'],
            "check": ['تحقق', 'هل لدي'],
            "add": ['أضف', 'اشتري', 'أحتاج']
        },
        "hi": {
            "search": ['खोज', 'ढूंढो', 'खोजो'],
            "remove": ['हटाओ', 'मिटाओ', 'निकालो'],
            "update": ['अद्यतन', 'बदलो'],
            "clear": ['साफ़', 'खाली'],
            "check": ['जांच', 'क्या मेरे पास'],
            "add": ['जोड़ो', 'खरीदो', 'मुझे चाहिए']
        },
        "ja": {
            "search": ['検索', '探す', '見つける'],
            "remove": ['削除', '取り除く'],
            "update": ['更新', '変更'],
            "clear": ['クリア', '空に'],
            "check": ['確認', '持っている'],
            "add": ['追加', '買う', '必要']
        },
        "ko": {
            "search": ['찾아', '검색', '찾기'],
            "remove": ['삭제', '제거'],
            "update": ['업데이트', '변경'],
            "clear": ['비우', '정리'],
            "check": ['확인', '있나'],
            "add": ['추가', '사', '필요해']
        },
        "zh": {
            "search": ['找', '搜索', '查找'],
            "remove": ['删除', '移除'],
            "update": ['更新', '修改'],
            "clear": ['清空', '清除'],
            "check": ['检查', '我有'],
            "add": ['添加', '买', '需要']
        }
    }
    keywords = keyword_groups.get(language_family, keyword_groups["en"])

    search_keywords = keywords["search"]
    remove_keywords = keywords["remove"]
    update_keywords = keywords["update"]
    clear_keywords = keywords["clear"]
    check_keywords = keywords["check"]
    add_keywords = keywords["add"]

    if any(p in text for p in clear_keywords):
        intent = "CLEAR"
        message = build_localized_message("CLEAR", item, quantity, language)
    elif any(p in text for p in check_keywords):
        intent = "CHECK"
        item = text
        for kw in check_keywords:
            item = item.replace(kw, '')
        item = item.strip()
        message = build_localized_message("CHECK", item, quantity, language)
    elif any(p in text for p in update_keywords):
        intent = "UPDATE"
        item = text
        for kw in update_keywords:
            item = item.replace(kw, '')
        item = item.strip()
        qty_match = re.search(r'\b(\d+)\b', text)
        if qty_match:
            quantity = int(qty_match.group(1))
        message = build_localized_message("UPDATE", item, quantity, language)
    elif any(p in text for p in search_keywords):
        intent = "SEARCH"
        item = text
        for kw in search_keywords:
            item = item.replace(kw, '')
        item = item.strip()
        price_patterns = {
            "en": r'(?:under|less than|below)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "es": r'(?:menos de|por debajo de|bajo)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "fr": r'(?:moins de|en dessous de|sous)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "de": r'(?:unter|unterhalb von|weniger als)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "it": r'(?:sotto|meno di|inferiore a)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "pt": r'(?:menos de|abaixo de|por baixo de)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "nl": r'(?:minder dan|onder|lager dan)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "ar": r'(?:أقل من|أدنى من|تحت)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "hi": r'(?:से कम|कम|नीचे)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "ja": r'(?:以下|より安く|下)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "ko": r'(?:이하|보다 저렴하게|아래)\s*\$?\s*(\d+(?:\.\d{2})?)',
            "zh": r'(?:少于|低于|以下)\s*\$?\s*(\d+(?:\.\d{2})?)'
        }
        price_match = re.search(price_patterns.get(language_family, price_patterns["en"]), text)
        if price_match:
            maxPrice = float(price_match.group(1))
            item = item.replace(price_match.group(0), '').strip()
        message = build_localized_message("SEARCH", item, quantity, language)
    elif any(p in text for p in remove_keywords):
        intent = "REMOVE"
        item = text
        for kw in remove_keywords:
            item = item.replace(kw, '')
        item = item.strip()
        message = build_localized_message("REMOVE", item, quantity, language)
    else:
        intent = "ADD"
        item = text
        for kw in add_keywords:
            item = item.replace(kw, '')
        item = item.strip()
        qty_match = re.search(r'\b(\d+)\b', item)
        if qty_match:
            quantity = int(qty_match.group(1))
            item = item.replace(qty_match.group(0), '').strip()
        message = build_localized_message("ADD", item, quantity, language)

    return {
        "intent": intent,
        "item": item,
        "quantity": quantity,
        "category": "other",
        "maxPrice": maxPrice,
        "message": message
    }

@app.post("/api/process-command", response_model=ProcessedCommand)
async def process_command(request: CommandRequest):
    data = None
    try:
        if GEMINI_API_KEY and GEMINI_API_KEY != "your_api_key_here":
            if USE_NEW_SDK:
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[SYSTEM_PROMPT, f"Language Code: {request.language}\nTranscript: \"{request.transcript}\""]
                )
            else:
                genai_old.configure(api_key=GEMINI_API_KEY)
                model = genai_old.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content([
                    {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
                    {"role": "user", "parts": [{"text": f"Language Code: {request.language}\nTranscript: \"{request.transcript}\""}]}
                ])
                
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            data = json.loads(raw_text.strip())
        else:
            raise Exception("No valid GEMINI_API_KEY provided")
            
    except Exception as e:
        print(f"AI Model Error (falling back to local parser): {e}")
        data = fallback_parser(request.transcript, request.language)
        
    # Build success message if missing
    if not data.get("message"):
        intent = data.get("intent", "UNKNOWN")
        item = data.get("item", "")
        qty = data.get("quantity", 1)
        
        msg = build_localized_message(intent, item, qty, request.language)
        data["message"] = msg

    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
