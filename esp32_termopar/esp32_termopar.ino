#include <BluetoothSerial.h>

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#include <max6675.h>

String dados = "";
float temperatura = 0.0;
float maxTemp = -1000.0;
float minTemp = 1000.0;

int SO_ = 4;
int CS_ = 0;
int SCK_ = 2;

MAX6675 sensor(SCK_, CS_, SO_);
BluetoothSerial SerialBT;

void setup() {
  
  Serial.begin(115200);
  SerialBT.begin("ESP32test");
  delay(2000);
}

void loop() {
  
  if (Serial.available()) {
    
    SerialBT.write(Serial.read());
  }
  
  if (SerialBT.available()) {
    
    Serial.write(SerialBT.read());
  }
  
  temperatura = sensor.readCelsius();
  
  if(temperatura > maxTemp) {
    
    maxTemp = temperatura;  
  }
  
  if(temperatura < minTemp) {
    
    minTemp = temperatura;  
  }
  
  dados = "Temp. = " + (String)temperatura + " C Max. = " + (String)maxTemp + " C Min. = " + (String)minTemp + '\n';

  SerialBT.print(dados);
  delay(5000);
}
