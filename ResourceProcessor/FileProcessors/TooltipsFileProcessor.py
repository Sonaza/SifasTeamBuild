
from ResourceProcessor import FileProcessorBase
import os
import htmlmin

class TooltipsFileProcessor(FileProcessorBase):
	comment_format    = "/* {} */"
	file_prologue     = "app.run(($templateCache) =>\n{"
	file_epilogue     = "});"
	indentation       = 1
	
	def needs_compilation(self, filepath):
		return True
	
	def compile(self, source_code, filepath):
		source_code = ''.join([x.strip() for x in source_code.split('\n')])
		source_code = htmlmin.minify(source_code)
		source_code = source_code.replace("'", "\\'")
		return f"$templateCache.put('tooltips/{os.path.basename(filepath)}', '{source_code}');"
		
	def minify(self, source_code, filepath):
		return source_code
