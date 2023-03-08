
from ResourceProcessor import FileProcessorBase
import sass
import csscompressor

class CSSFileProcessor(FileProcessorBase):
	comment_format      = "/* {} */"
	after_concatenation = ""
	
	scss_globals = """
	$member-ids: 8 5 6 1 3 4 7 2 9 107 106 109 101 102 105 103 104 108 209 202 203 210 201 207 205 212 208 206 204 211;
	"""
	
	def needs_compilation(self, filepath):
		return '.scss' in filepath
	
	def compile(self, source_code, filepath):
		if not source_code:
			return ''
		
		source_code = self.scss_globals + "\n" + source_code
		
		try:
			return sass.compile(string=source_code)
		except sass.CompileError as e:
			raise e
			
		return ''
	
	def minify(self, source_code, filepath):
		return csscompressor.compress(source_code, max_linelen=20480)
	
	# def fix_scss_bullshit(self, code):
	# 	def repl(m):
	# 		divide = lambda s, d: list(map(''.join, zip(*[iter(s)]*d)))
	# 		c = [int(x * (3 - len(x)), 16) for x in divide(m.group(1), len(m.group(1)) // 3)]
	# 		if len(c) == 4:
	# 			return f"rgba({c[0]}, {c[1]}, {c[2]}, {(c[3] / 255):0.3f})"
	# 		else:
	# 			return "#" + m.group(1)
		
	# 	pattern = re.compile(r'(?<=[^0-9a-f])#([0-9a-f]{3,8})(?=[^0-9a-f])', re.MULTILINE | re.IGNORECASE)
	# 	return pattern.sub(repl, code)
