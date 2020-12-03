import sys,os

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path)
from urdf2rai import urdf2rai

directory = sys.argv[1]

for root, dirs, files in os.walk(directory):
  for f in files:
    if f.endswith(".urdf"):
      filename = os.path.join(root, f)
      urdf2rai(filename)
