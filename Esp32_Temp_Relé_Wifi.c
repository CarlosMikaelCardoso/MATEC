#include <OneWire.h>
#include <DallasTemperature.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <SoftwareSerial.h>

#define E32_TX 16 // Pino TX do módulo E32
#define E32_RX 17 // Pino RX do módulo E32

// Defina os pinos e a rede
#define ONE_WIRE_BUS 15
#define RELAY_PIN 2  // Pino do relé

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
const char* ssid = "OpenWrt";
const char* password = "2003GERcom!@#$%";
const char* serverUrl = "http://192.168.1.150:5000/endpoint"; // URL do endpoint no Raspberry

bool alertSent = false; // Variável para rastrear se um alerta foi enviado

void setup() {
Serial.begin(9600);      // Inicializa a Serial para monitoramento
LoRaSerial.begin(9600);  // Inicializa a comunicação com o E32
Serial.println("Receptor iniciado!");
sensors.begin();
pinMode(RELAY_PIN, OUTPUT);
digitalWrite(RELAY_PIN, LOW);  // Relé desligado inicialmente
WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("Conectado ao WiFi!");
}

void loop() {
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"temperature\": " + String(tempC) + "}";
    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.println("Dados enviados com sucesso: " + payload);
    } else {
      Serial.println("Erro ao enviar os dados");
    }
    http.end();
  }

  // Lógica para enviar alerta
  if (tempC >= 30) {
    if (!alertSent) {
      Serial.println("Temperatura acima de 30°C! Enviando alerta.");
      digitalWrite(RELAY_PIN, HIGH);  // Liga o ventilador
      alertSent = true; // Marca que um alerta foi enviado
    }
  } else {
    if (alertSent) {
      Serial.println("Temperatura abaixo de 30°C! Enviando alerta.");
      digitalWrite(RELAY_PIN, LOW);  // Desliga o ventilador
      alertSent = false; // Reseta o estado quando a temperatura cai abaixo de 30°C
    }
  }

 // Lógica para enviar alerta
if (LoRaSerial.available()) {
    String message = LoRaSerial.readStringUntil('\n'); // Lê até a nova linha
    Serial.print("Mensagem recebida: ");
    Serial.println(message);
    
    // Verifica se a mensagem é sobre a queda de energia
    if (message.equals("Energia caiu")) {
        Serial.println("Alerta: Energia caiu! Enviando notificação via PushBullet.");
        
        // Envia notificação ao Raspberry
        if (WiFi.status() == WL_CONNECTED) {
            HTTPClient http;
            http.begin(serverUrl);
            http.addHeader("Content-Type", "application/json");
            
            String payload = "{\"power\": \"off\"}"; // Mensagem de queda de energia
            int httpResponseCode = http.POST(payload);
            
            if (httpResponseCode > 0) {
                Serial.println("Notificação de queda de energia enviada com sucesso!");
            } else {
                Serial.println("Erro ao enviar notificação de queda de energia");
            }
            http.end();
        }
    }
}
  delay(10000); // Espera de 10 segundos entre leituras
}
