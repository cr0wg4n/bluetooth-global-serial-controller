
import RPi.GPIO as gpio
import time
import os
import subprocess
import serial

motorA1 = 8
motorA2 = 10
motorB1 = 12
motorB2 = 16
pulsador = 33
modoArduino = True
echo = 35
trigger = 37


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

def distancia():
    gpio.output(trigger,True)   #Enviamos un pulso de ultrasonidos
    time.sleep(0.00001)              #Una pequena pausa
    gpio.output(trigger,False)  #Apagamos el pulso
    start = time.time()              #Guarda el tiempo actual mediante time.time()
    stop = 0
    while gpio.input(echo)==0:  #Mientras el sensor no reciba senal...
        start = time.time()          #Mantenemos el tiempo actual mediante time.time()
    while gpio.input(echo)==1:  #Si el sensor recibe senal...
        stop = time.time()           #Guarda el tiempo actual mediante time.time() en otra variable
    elapsed = stop-start             #Obtenemos el tiempo transcurrido entre envio y recepcion
    distancia = (elapsed * 34300)/2   #Distancia es igual a tiempo por velocidad partido por 2   D = (T x V)/2
    return distancia

def cambiarDeModo(chanel):
    global modoArduino
    modoArduino = not modoArduino

def ordenes(mensaje):
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
        if 'fren' in mensaje:
            frenar()

def reiniciarServiciosBluetooth():
    os.system('sudo pkill rfcomm')
    os.system('sudo service bluetooth restart')

try:
    time.sleep(20)
    gpio.setmode(gpio.BOARD)
    gpio.setup(motorA1,gpio.OUT)#motor izquierda
    gpio.setup(motorA2,gpio.OUT)
    gpio.setup(motorB1,gpio.OUT)#motor derecha
    gpio.setup(motorB2,gpio.OUT)
    gpio.setup(trigger,gpio.OUT)
    gpio.setup(echo,gpio.IN)
    gpio.output(trigger,False)
    gpio.setup(pulsador, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.add_event_detect(pulsador, gpio.RISING,callback=cambiarDeModo,bouncetime=2000)

    while True:
        if(modoArduino):
            print('<< modo arduino >>')
            os.system('espeak -ves modo_arduino')
            reiniciarServiciosBluetooth()
            time.sleep(2)
            if(not os.path.exists('/dev/rfcomm1')):
                os.system('rfcomm bind 1 98:D3:B1:FD:3B:27')
                time.sleep(0.5)
            try:
                conexion = serial.Serial('/dev/rfcomm1',9600,timeout=0.01)
            except:
                pass
            frenar()
            while True and conexion.isOpen():
                if(distancia() < 20):
                    frenar()
                try:
                    mensaje = conexion.readline()
                    if mensaje:
                        ordenes(mensaje)
                except:
                    conexion.close()
                    break
                if not modoArduino:
                    conexion.close()
                    break
        else:
            os.system('espeak -ves modo_celular')
            print('<< modo celular >>')
            time.sleep(2)
            ps = subprocess.Popen(['sudo','rfcomm','watch', 'hci0'])
            while True:
                if(os.path.exists('/dev/rfcomm0')):
                    print('conectado')
                    os.system('espeak -ves conexion_con_celular_exitosa')
                    break
                else:
                    print('sin conexion')
                    break
                time.sleep(1)
            try:
                conexion = serial.Serial('/dev/rfcomm0',9600,timeout=0.01)
            except:
                pass
            frenar()
            while True and conexion.isOpen():
                if(distancia() < 20):
                    frenar()
                try:
                    mensaje = conexion.readline()
                    if mensaje:
                        ordenes(mensaje)
                except:
                    conexion.close()
                    ps.terminate()
                    reiniciarServiciosBluetooth()
                    time.sleep(0.5)
                    break
                if modoArduino:
                    ps.terminate()
                    conexion.close()
                    reiniciarServiciosBluetooth()
                    time.sleep(0.5)
                    break

except (KeyboardInterrupt, SystemExit):
    gpio.cleanup()
    ps.terminate()
    reiniciarServiciosBluetooth()
    conexion.close()
