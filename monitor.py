import requests
from bs4 import BeautifulSoup
import datetime
import csv

# --- CONFIGURACIÓN ---
TOKEN = "8718780675:AAEwKA9NynqgFzarJkgPF7VxO4evGn1ho_k"
CHAT_ID = "1584135749"
SHEET_ID = "1JNJtdPuX9UjLP0Y85SvtgLAahyg94ouok3hixL_8HCI"

def obtener_expedientes_desde_google():
    url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        response = requests.get(url_csv)
        response.encoding = 'utf-8'
        lineas = response.text.splitlines()
        lector = csv.reader(lineas)
        # Saltamos la primera fila (encabezado) y limpiamos espacios
        return [fila[0].strip() for fila in lector if fila][1:]
    except:
        return []

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": mensaje, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, data=payload)

def revisar_estrados():
    # 1. Leer la lista del Excel de Google
    BUSQUEDA = obtener_expedientes_desde_google()
    
    if not BUSQUEDA:
        print("La lista de Google Sheets está vacía o no es pública.")
        return

    url_estrados = "https://www.tsjqroo.gob.mx/estrados/"
    
    # --- CONFIGURACIÓN PARA EVITAR EL BLOQUEO (USER-AGENT) ---
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.google.com/'
    }

    try:
        # Usamos una sesión para mantener las "cookies" y parecer más humanos
        session = requests.Session()
        response = session.get(url_estrados, headers=headers, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texto_web = soup.get_text().upper()
            
            # 2. Buscar coincidencias
            encontrados = [item for item in BUSQUEDA if item.upper() in texto_web]
            
            fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
            
            if encontrados:
                mensaje = f"⚖️ *¡Hola amor! Revisé los estrados de hoy ({fecha_hoy}):*\n\n"
                mensaje += "He encontrado novedades en estos expedientes:\n"
                for item in encontrados:
                    mensaje += f"📍 `{item}`\n"
                mensaje += f"\n🔗 [Clic aquí para ver el boletín]({url_estrados})\n"
                mensaje += "\n*¡Te deseo mucho éxito en todo lo que hagas hoy! Te quiero.* ❤️"
                enviar_telegram(mensaje)
            else:
                # Si prefieres que NO le llegue nada si no hay cambios, comenta la línea de abajo
                enviar_telegram(f"✅ *Revisión diaria ({fecha_hoy}):*\nNo hay novedades en tus casos hoy. ¡Que tengas un excelente día! ✨")
        else:
            print(f"El portal respondió con error: {response.status_code}")

    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    revisar_estrados()
