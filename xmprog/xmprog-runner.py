#!/usr/bin/python3 -B
#_______________________________________________________________________________
#
import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)
sys.path.append('%s/xmprog/generator' % XMPG_HOME)

from Example import *
from Generator import *

import os
import sys
import importlib
import re

import curses
import getch

from Example import *
#_______________________________________________________________________________
#
dryRun = False

currentDir = os.path.abspath('.')

referentiel = Example()     # Référentiel global

for (path, dirs, files) in os.walk(currentDir, topdown=False):
	for f in sorted(files):
		if not f.endswith('.ref-code.py'):
			continue

		filename = '%s/%s' % (path, f)
		dirname = os.path.dirname(filename)

		referentiel.loadSourceCode(filename)

for (path, dirs, files) in os.walk(currentDir, topdown=False):
	for f in sorted(files):
		if not f.endswith('.py') or '/ref-code/' in path or '/code-GEN/' in path:
			continue

		filename = '%s/%s' % (path, f)
		dirname = os.path.dirname(filename)
		basename = os.path.basename(filename)
		basenameSansExt = os.path.splitext(basename)[0]

		os.chdir(dirname)

		# Chargement du fichier .py en tant que Module (ce qui exécute le fichier)
		if dirname not in sys.path:
			sys.path.append(dirname)
		module = importlib.import_module(basenameSansExt)

		if hasattr(module.Referentiel, 'define'):
			module.Referentiel.define(referentiel)

		if hasattr(module.Referentiel, 'process'):
			module.Referentiel.process(referentiel)

os.chdir(currentDir)

Generator.generate(referentiel, dryRun=dryRun)
#_______________________________________________________________________________
#
import curses
import curses.textpad

class Screen(object):
	UP = -1
	DOWN = 1

	def __init__(self, items):
		""" Initialize the screen window

		Attributes
			window: A full curses screen window

			width: The width of `window`
			height: The height of `window`

			max_lines: Maximum visible line count for `result_window`
			top: Available top line position for current page (used on scrolling)
			bottom: Available bottom line position for whole pages (as length of items)
			current: Current highlighted line number (as window cursor)
			page: Total page count which being changed corresponding to result of a query (starts from 0)

			┌--------------------------------------┐
			|1. Item                               |
			|--------------------------------------| <- top = 1
			|2. Item                               |
			|3. Item                               |
			|4./Item///////////////////////////////| <- current = 3
			|5. Item                               |
			|6. Item                               |
			|7. Item                               |
			|8. Item                               | <- max_lines = 7
			|--------------------------------------|
			|9. Item                               |
			|10. Item                              | <- bottom = 10
			|                                      |
			|                                      | <- page = 1 (0 and 1)
			└--------------------------------------┘

		Returns
			None
		"""
		self.window = None

		self.width = 0
		self.height = 0

		self.init_curses()

		self.items = items

		self.max_lines = curses.LINES
		self.top = 0
		self.bottom = len(self.items)
		self.current = 0
		self.page = self.bottom // self.max_lines

		self.showEmptyValues = True # showValue(...): afficher les valeurs vides: None, {}, []

	def init_curses(self):
		"""Setup the curses"""
		self.window = curses.initscr()
		self.window.keypad(True)

		curses.noecho()
		curses.cbreak()
		curses.curs_set(0) #Hide cursor

		curses.start_color()
		curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)

		self.current = curses.color_pair(2)

		self.height, self.width = self.window.getmaxyx()

	def run(self):
		"""Continue running the TUI until get interrupted"""

		self.current = 1

		while True:
			ref = None
			os.system('clear')

			try:
				ref = self.input_stream()

				if ref is None:
					break
			except KeyboardInterrupt:
				pass
			finally:
				curses.endwin()

			if ref is not None:
				referentiel.showValue(ref, showEmpty=self.showEmptyValues)
				print('Appuyez sur une touche pour continuer...', end='%s%s' % ('\r', 5 * '\t'))
				c = getch.getch()

				if c == 'q':
					print()
					break

	def input_stream(self):
		"""Waiting an input and run a proper method according to type of input"""
		while True:
			self.display()

			ch = self.window.getch()

			if ch == curses.KEY_UP:
				self.scroll(self.UP)
			elif ch == curses.KEY_DOWN:
				self.scroll(self.DOWN)
			elif ch == 339  :
				self.scroll(-4)
			elif ch == 338:
				self.scroll(+4)
			elif ch == curses.KEY_LEFT:
				self.paging(self.UP)
			elif ch == curses.KEY_RIGHT:
				self.paging(self.DOWN)
			elif ch == ord('\n'):
				ref = self.items[self.current - 1]
				return ref
			elif ch == 9:   # [TAB]
				self.showEmptyValues = not self.showEmptyValues
			elif ch in (ord('Q'), ord('q')):
				return None

	def scroll(self, direction):
		"""Scrolling the window when pressing up/down arrow keys"""
		self.current += direction
		self.current = min(max(1, self.current), len(self.items))

		self.top = self.max_lines * ((self.current - 1) // self.max_lines)

	def paging(self, direction):
		"""Paging the window when pressing left/right arrow keys"""
		if ((direction > 0 and self.top + self.max_lines >= len(self.items))
		  or (direction < 0 and self.top - self.max_lines < 0)
		  or len(self.items) < self.max_lines):
			return

		self.top += direction * self.max_lines
		self.current += direction * self.max_lines
		self.current = min(self.current, len(self.items))

	def display(self):
		"""Display the items on window"""
		self.window.erase()
		indicateur = '+' if self.showEmptyValues is True else '-'

		for idx, item in enumerate(self.items[self.top:self.top + self.max_lines]):
			# Highlight the current cursor line
			if self.top + idx + 1 == self.current:
				self.window.addstr(idx, 0, '%6d. %s %s' % (self.top + idx + 1, indicateur, item), curses.color_pair(2))
			else:
				self.window.addstr(idx, 0, '%6d. %s %s' % (self.top + idx + 1, indicateur, item), curses.color_pair(1))
		# self.window.refresh()

def main():
	os.system('clear')
	items = [ ref for ref in sorted(referentiel.repository.keys()) ]
	screen = Screen(items)
	screen.run()

if __name__ == '__main__':
	main()
