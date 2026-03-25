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
        return [fila[0].strip() for fila in lector if fila][1:]
    except:
        return []

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})

def revisar_estrados():
    BUSQUEDA = obtener_expedientes_desde_google()
    if not BUSQUEDA:
        print("La lista de Google Sheets está vacía.")
        return

    # Usamos un servicio de 'CORS Proxy' para saltar el bloqueo regional
    # Este servicio actúa como un túnel para entrar a páginas de gobierno
    url_objetivo = "https://www.tsjqroo.gob.mx/estrados/"
    proxy_url = f"https://api.allorigins.win/get?url={url_objetivo}"

    try:
        print("Intentando conectar a través del túnel...")
        response = requests.get(proxy_url, timeout=30)
        
        if response.status_code == 200:
            # El contenido viene dentro de un JSON llamado 'contents'
            html_puro = response.json()['contents']
            soup = BeautifulSoup(html_puro, 'html.parser')
            texto_web = soup.get_text().upper()
            
            encontrados = [item for item in BUSQUEDA if item.upper() in texto_web]
            fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
            
            if encontrados:
                mensaje = f"⚖️ *¡Hola amor! Encontré novedades hoy ({fecha_hoy}):*\n\n"
                for item in encontrados:
                    mensaje += f"📍 `{item}`\n"
                mensaje += f"\n🔗 [Ver Boletín]({url_objetivo})\n"
                mensaje += "\n*¡Te quiero y te deseo un gran día!* ❤️"
                enviar_telegram(mensaje)
            else:
                # Si quieres que siempre le llegue algo, descomenta la línea de abajo:
                enviar_telegram(f"✅ *Revisión diaria ({fecha_hoy}):*\nNo hay novedades en tus casos hoy. ¡Mucho éxito! ✨")
                print("No se encontraron coincidencias.")
        else:
            print(f"El túnel falló con código: {response.status_code}")

    except Exception as e:
        print(f"Error crítico de conexión: {e}")

if __name__ == "__main__":
    revisar_estrados()
