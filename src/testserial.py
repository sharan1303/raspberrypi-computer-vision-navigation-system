import serial

s = serial.Serial('COM4', 9600, timeout=1)
asc = 'Hello World'
s.write(asc.encode())
s.close()