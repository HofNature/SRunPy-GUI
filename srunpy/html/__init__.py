import importlib.resources
from os import path
from srunpy import html
with importlib.resources.path(html, 'index.html') as HtmlFile:
	WebRoot = path.dirname(HtmlFile)
	print('Resource Path:', WebRoot)
