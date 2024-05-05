#include <Wire.h>
#include <ADXL345.h>  // ADXL345 Accelerometer Library
#include <ITG3200.h>  // ITG3200 Gyroscope Library

ADXL345 acc; // Instance of the ADXL345 accelerometer library
ITG3200 gyro = ITG3200();
float gx, gy, gz;
float gx_rate, gy_rate, gz_rate;
int ix, iy, iz;
float anglegx=0.0, anglegy=0.0, anglegz=0.0;
int ax, ay, az;  
int rawX, rawY, rawZ;
float X, Y, Z;
float rollrad, pitchrad;
float rolldeg, pitchdeg;
int error = 0; 
float aoffsetX, aoffsetY, aoffsetZ;
float goffsetX, goffsetY, goffsetZ;
unsigned long time, looptime;
// Define pins for the flex sensors
const int flexPins[] = {A0, A1, A2, A3, A4}; // Pins connected to voltage divider outputs
const int numSensors = 5; // Number of sensors

// Constants
const float VCC = 5;           // Voltage at Arduino 5V line
const float R_DIV = 47000.0;   // Resistor used to create a voltage divider
const float flatResistance = 25000.0; // Resistance when flat
const float bendResistance = 100000.0; // Resistance at 90 degrees
float alpha = 0.5; // Smoothing factor
float filteredX = 0, filteredY = 0, filteredZ = 0;

void filterAccelData(int rawX, int rawY, int rawZ) {
  filteredX = alpha * filteredX + (1 - alpha) * (rawX / 256.00);
  filteredY = alpha * filteredY + (1 - alpha) * (rawY / 256.00);
  filteredZ = alpha * filteredZ + (1 - alpha) * (rawZ / 256.00);
}


void setup(){
  Serial.begin(9600);
  acc.powerOn();
  gyro.init(ITG3200_ADDR_AD0_LOW);
  calibrateSensors();  // Call the enhanced calibration function

  for (int i = 0; i < numSensors; i++) {
    pinMode(flexPins[i], INPUT);
    pinMode(flexPins[i], INPUT);
  }
  acc.powerOn();
  // Calibrate accelerometer
  for (int i = 0; i <= 200; i++) {
    acc.readAccel(&ax, &ay, &az);
    if (i == 0) {
      aoffsetX = ax;
      aoffsetY = ay;
      aoffsetZ = az;
    }
    if (i > 1) {
      aoffsetX = (ax + aoffsetX) / 2;
      aoffsetY = (ay + aoffsetY) / 2;
      aoffsetZ = (az + aoffsetZ) / 2;
    }
  }
  // Calibrate gyroscope
  for (int i = 0; i <= 200; i++) {
    gyro.readGyro(&gx,&gy,&gz);
    if (i == 0) {
      goffsetX = gx;
      goffsetY = gy;
      goffsetZ = gz;
    }
    if (i > 1) {
      goffsetX = (gx + goffsetX) / 2;
      goffsetY = (gy + goffsetY) / 2;
      goffsetZ = (gz + goffsetZ) / 2;
    }
  }
  delay(1000);
  gyro.init(ITG3200_ADDR_AD0_LOW);
}

void loop(){
  acc.readAccel(&ax, &ay, &az); // Read accelerometer values
  rawX = ax - aoffsetX;
  rawY = ay - aoffsetY;
  rawZ = az - aoffsetZ;
  filterAccelData(rawX, rawY, rawZ); // Apply filtering

  rollrad = atan(filteredY / sqrt(filteredX * filteredX + filteredZ * filteredZ));
  pitchrad = atan(filteredX / sqrt(filteredY * filteredY + filteredZ * filteredZ));
  rolldeg = 180 * rollrad / PI;
  pitchdeg = 180 * pitchrad / PI;
  for (int i = 0; i < numSensors; i++) {
    int ADCflex = analogRead(flexPins[i]);
    float Vflex = ADCflex * VCC / 1023.0;
    float Rflex = R_DIV * (VCC / Vflex - 1.0);
    float angle = map(Rflex, flatResistance, bendResistance, 0, 90.0);
    
    Serial.print(angle);
    Serial.print(",");
  }
  delay(100);
  // Accelerometer angle calculations
  time = millis();
  acc.readAccel(&ax, &ay, &az); // Read accelerometer values
  rawX = ax - aoffsetX;
  rawY = ay - aoffsetY;
  rawZ = az - aoffsetZ;
  X = rawX / 256.00;
  Y = rawY / 256.00;
  Z = rawZ / 256.00;
  rollrad = atan(Y / sqrt(X*X + Z*Z));
  pitchrad = atan(X / sqrt(Y*Y + Z*Z));
  rolldeg = 180 * rollrad / PI;
  pitchdeg = 180 * pitchrad / PI;

  // Gyroscope rate calculations
  gyro.readGyro(&gx,&gy,&gz);
  looptime = millis() - time;
  gx_rate = (gx - goffsetX) / 14.375;
  gy_rate = (gy - goffsetY) / 14.375;
  gz_rate = (gz - goffsetZ) / 14.375;

  anglegx += gx_rate * looptime;
  anglegy += gy_rate * looptime;
  anglegz += gz_rate * looptime;

  // Output accelerometer and gyroscope angles
  Serial.print(rolldeg);
  Serial.print(",");
  Serial.print(pitchdeg);
  Serial.println(",");
  delay(100);
}
void calibrateSensors() {
  long axSum = 0, aySum = 0, azSum = 0;
  long gxSum = 0, gySum = 0, gzSum = 0;
  const int calibrationReadings = 400;
  const int discardInitialReadings = 20;

  for (int i = 0; i < discardInitialReadings + calibrationReadings; i++) {
    acc.readAccel(&ax, &ay, &az);
    gyro.readGyro(&gx, &gy, &gz);

    if (i >= discardInitialReadings) { // Start accumulating valid readings
      axSum += ax;
      aySum += ay;
      azSum += az;
      gxSum += gx;
      gySum += gy;
      gzSum += gz;
    }
    delay(5); // Short delay to allow sensor readings to stabilize
  }

  aoffsetX = axSum / calibrationReadings;
  aoffsetY = aySum / calibrationReadings;
  aoffsetZ = azSum / calibrationReadings;
  goffsetX = gxSum / calibrationReadings;
  goffsetY = gySum / calibrationReadings;
  goffsetZ = gzSum / calibrationReadings;
  Serial.println("Calibration Complete");
}

