// pin that the sensor is attached to
const int analogPin = A0;
// pin that the LEDs are attached to
const int ledPin = 2;
// low uT threshold level
const float threshold_low = -100.0;
// high uT threshold level
const float threshold_high = 100.0;


void setup()
{
  // initialize the LED pin as an output
  pinMode(ledPin, OUTPUT);

  // initialize serial communications
  Serial.begin(9600);
}

void loop()
{
  // reads the sensor Vout, converts the input to a value between 0 and 1023
  int analogValue = analogRead(analogPin);

  // converts analog value to voltage level 0 V to 5 V
  float V_meter = analogValue*(5.0/1023.0);

  // converts V_meter to "Vout", which is referenced to 2.5 V internal reference
  float V_out = V_meter-2.478;

  // converts V_out to magnetic field value in uT
  float H_field = (V_out*1000.0*1000.0)/(4.0*12.2*100.0);

  // print the H field value:
  Serial.println(H_field);

  // if the H field is greater than high threshold OR less than low threshold,
  // turn on the LEDs, otherwise leave them off:
  if (H_field > threshold_high || H_field < threshold_low)
  {
    digitalWrite(ledPin, HIGH);
  }
  else
  {
    digitalWrite(ledPin,LOW);
  }

  // delay in between reads for stability
  delay(500);
}
