import os
import subprocess
import time

try:
 ps = subprocess.Popen(['sudo','rfcomm','watch', 'hci0'])
 while True:
  if(os.path.exists('/dev/rfcomm0')):
   print('conectado')
  else:
   print('sin conexion')
  time.sleep(1)

except (KeyboardInterrupt, SystemExit):
 ps.terminate()
