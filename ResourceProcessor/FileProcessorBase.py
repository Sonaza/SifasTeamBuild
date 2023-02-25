
from colorama import Fore, Style

class FileProcessorBase():
	comment_format       = "/* {} */"
	file_prologue        = ""
	file_epilogue        = ""
	before_concatenation = ""
	after_concatenation  = ""
	indentation          = 0
	
	def needs_compilation(self, filepath):
		raise NotImplementedError()
	
	def compile(self, source_code, filepath):
		raise NotImplementedError()
		
	def minify(self, source_code, filepath):
		raise NotImplementedError()
	
	def process(self, input_files, output_file, minify=True):
		compiled_code   = []
		unminified_size = 0
		minified_size   = 0
		
		for input_filepath in input_files:
			print(f"    {Fore.WHITE}{Style.BRIGHT}{input_filepath:<57}{Style.RESET_ALL}  ", end='')
			
			try:
				source_code = open(input_filepath, "r", encoding="utf-8").read()
			except:
				print(f"  {Fore.RED}Failed to open file...{Style.RESET_ALL}")
				continue
				
			if self.needs_compilation(input_filepath):
				print(f"  {Fore.MAGENTA}{Style.BRIGHT}Compiling...{Style.RESET_ALL}", end='')
				try:
					source_code = self.compile(source_code, input_filepath)
				except Exception as e:
					print(f"  {Fore.RED}Failed! ({type(e).__name__})")
					print()
					print("----------------------------------------------------------------------------------------------")
					print(str(e))
					print("----------------------------------------------------------------------------------------------")
					
					import traceback
					print(traceback.format_exc())
					
					print("----------------------------------------------------------------------------------------------")
					print(f"{Style.RESET_ALL}")
					return False
			
			if minify:
				print(f"  {Fore.BLUE}{Style.BRIGHT}Minifying...{Style.RESET_ALL}", end='')
				unminified_size += len(source_code)
				source_code = self.minify(source_code, input_filepath)
				minified_size += len(source_code)
			
			print(f"  {Fore.GREEN}{Style.BRIGHT}Done!{Style.RESET_ALL}")
			compiled_code.append((input_filepath, source_code))
		
		if minify:
			print(f"    {Fore.YELLOW}Minify reduced file size from {unminified_size / 1024:.2f} KB to {minified_size / 1024:.2f} KB. Yay!{Style.RESET_ALL}")
		
		indentation = ''
		if isinstance(self.indentation, int) and self.indentation > 0:
			indentation = '\t' * self.indentation
		elif isinstance(self.indentation, str):
			indentation = self.indentation
		
		with open(output_file, "w", encoding="utf-8") as file:	
			if self.file_prologue:
				file.write(self.file_prologue + "\n")
				
			for source_path, source_code in compiled_code:
				file.write(indentation)
				file.write(self.comment_format.format(source_path))
				file.write("\n")
				
				if self.before_concatenation:
					file.write(indentation)
					file.write(self.before_concatenation)
					file.write("\n")
					
				file.write(indentation)
				file.write(source_code)
				file.write("\n")
				
				file.write(self.after_concatenation)
				file.write("\n")
				
				file.flush()
				
			if self.file_epilogue:
				file.write(self.file_epilogue + "\n")
		
