import requests
from bs4 import BeautifulSoup
import datetime

# --- CONFIGURACIÓN (No compartas estos datos con nadie) ---
TOKEN = "8718780675:AAEwKA9NynqgFzarJkgPF7VxO4evGn1ho_k"
CHAT_ID = "1584135749"

# --- LISTA DE BÚSQUEDA ---
# Puedes agregar todos los que quieras, separados por comas.
BUSQUEDA = [
    "1045/2025", 
    "520/2026", 
    "NOMBRE_DE_ELLA", # Reemplaza por su nombre completo en mayúsculas
    "CLIENTE_ESPECIFICO"
]

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error al enviar Telegram: {e}")

def revisar_estrados():
    url = "https://www.tsjqroo.gob.mx/estrados/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 1. Intentamos leer el portal de Quintana Roo
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Portal no disponible (Status: {response.status_code})")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        texto_web = soup.get_text().upper()
        
        # 2. Buscamos coincidencias
        encontrados = [item for item in BUSQUEDA if item.upper() in texto_web]
        
        # 3. Construimos el mensaje "Romántico/Profesional"
        fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
        
        if encontrados:
            mensaje = f"⚖️ *¡Hola amor! Revisé los estrados de hoy ({fecha_hoy}):*\n\n"
            mensaje += "He encontrado novedades en estos expedientes:\n"
            for item in encontrados:
                mensaje += f"📍 `{item}`\n"
            mensaje += f"\n🔗 [Clic aquí para ver el boletín]({url})\n"
            mensaje += "\n*¡Te deseo mucho éxito en todo lo que hagas hoy! Te quiero.* ❤️"
        else:
            # Mensaje discreto si no hay nada, para que sepa que el bot sí trabajó
            mensaje = f"✅ *Todo tranquilo hoy ({fecha_hoy}).*\nRevisé los estrados y no hay novedades para tus casos. ¡Que tengas un día excelente! ✨"
            
        enviar_telegram(mensaje)

    except Exception as e:
        print(f"Ocurrió un error técnico: {e}")

if __name__ == "__main__":
    revisar_estrados()
