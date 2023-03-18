
from ResourceProcessor import FileProcessorBase
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Type, Any

@dataclass
class ProcessorTask:
	name: str
	
	file_processor: Optional[Type[FileProcessorBase]] = field(default_factory=lambda: None)
	
	pre_command: Optional[List[str]] = field(default_factory=lambda: None)
	post_command: Optional[List[str]] = field(default_factory=lambda: None)
	
	watch_directory: str = field(default_factory=str)
	watched_files: List[str] = field(default_factory=list)
	
	input_files: Optional[List[str]] = field(default_factory=lambda: None)
	output_file: Optional[str] = field(default_factory=lambda: None)
	
	depends_on: List[str] = field(default_factory=list)
	on_complete_run: List[str] = field(default_factory=list)
	
	def __post_init__(self):
		if self.file_processor != None:
			if not issubclass(self.file_processor, FileProcessorBase):
				raise ValueError("File processor must be a class type inherited from FileProcessorBase.")
			
			if not self.input_files or not self.output_file:
				raise ValueError("File processor task must have input files and an output file.")
			
			self.output_file = self.output_file.replace('\\', '/')
		
		if not self.file_processor and not self.pre_command and not self.post_command:
			raise ValueError("Task must have a defined file processor or command.")
		
	def has_file_processor(self) -> bool:
		return bool(self.file_processor)

	def has_command(self) -> bool:
		return bool(self.pre_command) or bool(self.post_command)

	def has_pre_command(self) -> bool:
		return bool(self.pre_command)
		
	def has_post_command(self) -> bool:
		return bool(self.post_command)

