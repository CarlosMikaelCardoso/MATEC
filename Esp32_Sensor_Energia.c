#include <SoftwareSerial.h>

#define E32_TX 17 // Pino TX do módulo E32
#define E32_RX 16 // Pino RX do módulo E32
#define ANALOG_PIN 34 // Pino analógico para leitura do ZMPT101B

SoftwareSerial LoRaSerial(E32_RX, E32_TX); // Cria uma instância de SoftwareSerial

void setup() {
  Serial.begin(9600);      // Inicializa a Serial para monitoramento
  LoRaSerial.begin(9600);  // Inicializa a comunicação com o E32
  pinMode(ANALOG_PIN, INPUT); // Define o pino analógico como entrada
  Serial.println("Transmissor de Energia iniciado...");
  delay(1000);
}

void loop() {
  // Lê a tensão do pino analógico
  int sensorValue = analogRead(ANALOG_PIN);
  // Converte o valor lido para a tensão correspondente (ajuste o fator de escala conforme necessário)
  float voltage = sensorValue * (5.0 / 1023.0); // Assumindo 5V como referência

  // Verifica se a tensão está abaixo de um certo limite
  if (voltage < 1.0) { // Ajuste o limite conforme necessário
    Serial.println("Energia caiu! Enviando mensagem...");
    LoRaSerial.println("Energia caiu"); // Envia a mensagem de alerta
    delay(5000); // Aguarda um tempo antes de verificar novamente
  }

  delay(1000); // Delay para evitar sobrecarga no loop
}
