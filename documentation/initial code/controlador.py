import RPi.GPIO as gpio
import time
import os
import serial

motorA1 = 8
motorA2 = 10
motorB1 = 12
motorB2 = 16
def girarIzquierda():
 print('giro izquieda')
 gpio.output(motorA1,gpio.HIGH)
 gpio.output(motorA2,gpio.LOW)
 gpio.output(motorB1,gpio.LOW)
 gpio.output(motorB2,gpio.LOW)

def girarDerecha():
 print('giro derecha')
 gpio.output(motorB1,gpio.HIGH)
 gpio.output(motorB2,gpio.LOW)
 gpio.output(motorA1,gpio.LOW)
 gpio.output(motorA2,gpio.LOW)

def avanzar():
 print('avanzo')
 gpio.output(motorA1,gpio.HIGH)
 gpio.output(motorA2,gpio.LOW)
 gpio.output(motorB1,gpio.HIGH)
 gpio.output(motorB2,gpio.LOW)

def retroceder():
 print('retro')
 gpio.output(motorA1,gpio.LOW)
 gpio.output(motorA2,gpio.HIGH)
 gpio.output(motorB1,gpio.LOW)
 gpio.output(motorB2,gpio.HIGH)

def frenar():
 print('freno')
 gpio.output(motorA1,gpio.LOW)
 gpio.output(motorA2,gpio.LOW)
 gpio.output(motorB1,gpio.LOW)
 gpio.output(motorB2,gpio.LOW)

try:
 if(not os.path.exists('/dev/rfcomm1')):
  os.system('rfcomm bind 1 98:D3:B1:FD:3B:27')
 conexion = serial.Serial('/dev/rfcomm1',9600,timeout=0.01)
 gpio.setmode(gpio.BOARD)
 gpio.setup(motorA1,gpio.OUT)#motor izquierda
 gpio.setup(motorA2,gpio.OUT)
 gpio.setup(motorB1,gpio.OUT)#motor derecha
 gpio.setup(motorB2,gpio.OUT)
 frenar()
 while True:
  mensaje = conexion.readline()
  if mensaje:
   print(mensaje)
   if 'arr' in mensaje:
    avanzar()
   if 'aba' in mensaje:
    retroceder()
   if 'der' in mensaje:
    girarDerecha()
   if 'izq' in mensaje:
    girarIzquierda()

except (KeyboardInterrupt, SystemExit):
 gpio.cleanup()
 conexion.close()
