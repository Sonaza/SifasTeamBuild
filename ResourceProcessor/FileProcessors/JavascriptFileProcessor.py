
from ResourceProcessor import FileProcessorBase
from rjsmin import jsmin

class JavascriptFileProcessor(FileProcessorBase):
	file_prologue       = "'use strict';\n"
	comment_format      = "/***********************************************\n *  {}\n */"
	after_concatenation = ";"
	
	def needs_compilation(self, filepath):
		return False
	
	def compile(self, source_code, filepath):
		return source_code
		
	def minify(self, source_code, filepath):
		minified = jsmin(source_code)
		# minified = ' '.join([line.strip() for line in minified.split('\n')])
		return minified
