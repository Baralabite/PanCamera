CON

  _clkmode = xtal1 + pll16x
  _xinfreq = 5_000_000

OBJ

  Servo: "Servo32v9"
  Serial: "FullDuplexSerialPlus"

PUB Main | rx

  Servo.start
  Servo.ramp
  Serial.start(31, 30, 0, 115200)

  repeat
    rx := Serial.rxDec
    Servo.SetRamp(0, (rx*10)+600, 150)
