from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuração para notificar via Pushbullet
PUSHBULLET_API_KEY = "o.GDsMyFtRG4IVAfvpgVJKRnyHKiVYjZuV"  # Insira sua chave de API aqui
temperature_alert_sent = False  # Variável de controle para o envio da notificação de temperatura
power_alert_sent = False  # Variável de controle para o envio do alerta de queda de energia
sound_alert_sent = False  # Variável de controle para o envio do alerta de som

def send_push_notification(title, body):
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {
        "Access-Token": PUSHBULLET_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "type": "note",
        "title": title,
        "body": body
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("Notificação enviada com sucesso!")
    else:
        print("Falha ao enviar notificação:", response.status_code, response.text)

@app.route('/endpoint', methods=['POST'])
def receive_data():
    global temperature_alert_sent, power_alert_sent, sound_alert_sent
    
    data = request.get_json()
    
    if data:
        # Verifica alerta de temperatura
        if "temperature" in data:
            temperature = data["temperature"]
            print(f"Temperatura recebida: {temperature}°C")
            
            if temperature >= 30 and not temperature_alert_sent:
                print("Alerta: Temperatura acima de 30°C!")
                send_push_notification("Alerta de Temperatura", f"Temperatura chegou a {temperature}°C!, Acionando Ventilador")
                temperature_alert_sent = True  # Marca que o alerta foi enviado
            elif temperature < 30 and temperature_alert_sent:
                print("Alerta: Temperatura abaixo de 30°C!")
                send_push_notification("Alerta de Temperatura", f"Temperatura diminuída para {temperature}°C!, Ventilador Desligado")
                temperature_alert_sent = False  # Reseta o estado quando a temperatura cai abaixo de 30°C
        
        # Verifica alerta de queda de energia
        if "power" in data and data["power"] == "off":
            print("Alerta: Queda de energia detectada!")
            if not power_alert_sent:
                send_push_notification("Alerta de Queda de Energia", "A energia caiu!")
                power_alert_sent = True  # Marca que o alerta foi enviado
                
        # Verifica alerta de som
        if "sound" in data and data["sound"] == "detected":
            print("Alerta: Som detectado!")
            if not sound_alert_sent:
                send_push_notification("Alerta de Som", "Um som foi detectado!")
                sound_alert_sent = True  # Marca que o alerta de som foi enviado
        elif "sound" in data and data["sound"] != "detected":
            sound_alert_sent = False  # Reseta o alerta de som quando não há som detectado
            
        return jsonify({"status": "success"}), 200
    
    else:
        return jsonify({"status": "error", "message": "Dados inválidos"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
