# For getting terminal on localhost at port 10000

# Installation of colabxterm by !pip install colab-xterm
from colabxterm import notebook
from ngrok_ import async_tasks

async_tasks()

try:
  import IPython
except Exception as e:
  print("The error is ", e)

# This would start off a local server on VM which should be tunneled through ngrok to access it
notebook._xterm_magic('')