from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuração para notificar via Pushbullet
PUSHBULLET_API_KEY = "o.GDsMyFtRG4IVAfvpgVJKRnyHKiVYjZuV"  # Insira sua chave de API aqui
temperature_alert_sent = False  # Variável de controle para o envio da notificação
power_alert_sent = False  # Variável de controle para o envio do alerta de queda de energia

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
    global temperature_alert_sent
    global power_alert_sent
    
    data = request.get_json()
    
    if data and "temperature" in data:
        temperature = data["temperature"]
        print(f"Temperatura recebida: {temperature}°C")
        
        if temperature >= 30 and not temperature_alert_sent:
            print("Alerta: Temperatura acima de 30°C!")
            send_push_notification("Alerta de Temperatura", f"Temperatura chegou a {temperature}°C!")
            temperature_alert_sent = True  # Marca que o alerta foi enviado
        elif temperature < 30 and temperature_alert_sent:
            print("Alerta: Temperatura abaixo de 30°C!")
            send_push_notification("Alerta de Temperatura", f"Temperatura diminuída para {temperature}°C!")
            temperature_alert_sent = False  # Reseta o estado quando a temperatura cai abaixo de 30°C
            
        return jsonify({"status": "success"}), 200
    
    elif data and "power" in data and data["power"] == "off":
        print("Alerta: Queda de energia detectada!")
        if not power_alert_sent:
            send_push_notification("Alerta de Queda de Energia", "A energia caiu!")
            power_alert_sent = True  # Marca que o alerta foi enviado
        return jsonify({"status": "success"}), 200
    
    else:
        return jsonify({"status": "error", "message": "Dados inválidos"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
