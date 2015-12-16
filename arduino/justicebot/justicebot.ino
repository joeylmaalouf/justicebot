#include <Servo.h>

Servo left, right;
char prev_data[2] = "h";
char serial_data[2] = "h";
byte LOOP_DELAY = 20;
byte LEFT_MOTOR_PORT = 8, RIGHT_MOTOR_PORT = 9;
byte STATIONARY = 0;
byte FORWARDS_MAX = 10, FORWARDS_MIN = 100, FORWARDS_STEP = -10;
byte BACKWARDS_MAX = 170, BACKWARDS_MIN = 80, BACKWARDS_STEP = 10;
byte forwards = FORWARDS_MIN, backwards = BACKWARDS_MIN;

void setup()
{
  left.attach(LEFT_MOTOR_PORT);
  right.attach(RIGHT_MOTOR_PORT);
  Serial.begin(9600);
}

void loop()
{  
  if (Serial.available())
  {
    memcpy(prev_data, serial_data, sizeof(serial_data));
    Serial.readBytes(serial_data, 1);
  }
  Serial.println(serial_data);

  // set motor power based on the input
  if (serial_data[0] == 'u')
  {
    left.write(forwards);
    right.write(backwards);
  }
  else if (serial_data[0] == 'd')
  {
    left.write(backwards);
    right.write(forwards);
  }
  else if (serial_data[0] == 'l')
  {
    left.write(forwards);
    right.write(forwards);
  }
  else if (serial_data[0] == 'r')
  {
    left.write(backwards);
    right.write(backwards);
  }
  else if (serial_data[0] == 'h')
  {
    left.write(STATIONARY);
    right.write(STATIONARY);
  }
  else if (serial_data[0] == 'f')
  {
    forwards = min(FORWARDS_MAX, forwards + FORWARDS_STEP);
    backwards = min(BACKWARDS_MAX, backwards + BACKWARDS_STEP);
  }
  else if (serial_data[0] == 's')
  {
    forwards = max(FORWARDS_MIN, forwards - FORWARDS_STEP);
    backwards = max(BACKWARDS_MIN, backwards - BACKWARDS_STEP);
  }

  delay(LOOP_DELAY);
}
