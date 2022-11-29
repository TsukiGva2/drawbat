from sys import stdout
from time import sleep

import subprocess
import threading
import blessed
import psutil
import signal

import cfonts

FULL = 3 # 3 charging bars

class Killer:
	kill_now = threading.Event()

	def __init__(self):
		signal.signal(signal.SIGTERM, self.exit_grace)
		signal.signal(signal.SIGINT, self.exit_grace)

	def exit_grace(self, *args):
		self.kill_now.set()

def get_battery_str(charge):
	bat = "("
	chars = int(FULL * charge)
	bat += "=" * chars
	bat += " " * int(FULL - chars) + "): " + str(int(charge*100)) + "%"

	return bat

def main():
	term = blessed.Terminal()

	killer = Killer()

	with term.cbreak(), term.hidden_cursor():
		while not killer.kill_now.is_set():
			print(term.clear)

			charge = 0
			if not psutil.OPENBSD:
				battery = psutil.sensors_battery()
				charge = battery.percent / 100
			else:
				apm = subprocess.Popen(("apm",), stdout=subprocess.PIPE)
				output = subprocess.check_output(('awk', 'NR==1{print$4}'), stdin=apm.stdout)

				charge = int(output[:-2]) / 100

			bat = get_battery_str(charge)

			colors = ["green"]
			if charge <= 0.5 and charge > 0.2:
				colors = ["yellow"]
			elif charge <= 0.2:
				colors = ["red"]
			colors.append("black")

			output = cfonts.render(bat, align='center', colors=colors)
			print(output,end="")

			stdout.flush()

			killer.kill_now.wait(10)

if __name__ == "__main__":
	main()

