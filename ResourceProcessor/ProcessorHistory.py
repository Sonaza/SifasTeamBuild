from Common import Utility
import os
import json
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Type, Any

from .ProcessorTask import ProcessorTask

class ProcessorHistory:
	
	def __init__(self, history_file: str):
		self.processor_history = {}
		
		self.history_file = history_file
		self.processor_history_loaded = self.load()
	
	
	def is_loaded(self):
		return self.processor_history_loaded
		
		
	def load(self):
		if os.path.exists(self.history_file):
			try:
				with open(self.history_file, "r") as f:
					self.processor_history = json.load(f)
				
				for task_name, data in self.processor_history.items():
					data['last_processed'] = datetime.fromisoformat(data['last_processed'])
					data['input_files']    = set(data['input_files'])
				
				return True
				
			except Exception as e:
				self.processor_history = {}
				
		return False
		
		
	def save(self):
		if not isinstance(self.processor_history, dict):
			return False
			
		def json_serialize(obj):
		    if isinstance(obj, (datetime)):
		        return obj.isoformat()
		    if isinstance(obj, (set)):
		        return list(obj)
		    raise TypeError(f"Type {type(obj)} not serializable")
		
		with open(self.history_file, "w") as f:
			json.dump(self.processor_history, f, default=json_serialize)
		
		return True
	
	
	def get_task(self, task_name: str) -> Optional[ProcessorTask]:
		if task_name not in self.processor_history:
			return None
			
		required_keys = ('last_processed', 'input_files', 'output_file')
		if not Utility.contains_all(self.processor_history[task_name], required_keys):
			return None
		
		return self.processor_history[task_name]
	
	
	def mark(self, task_name: str, input_files: List[str], output_file: str):
		# Normalise file path slashes on windows
		if Utility.is_windows():
			input_files = [file.replace('\\', '/') for file in input_files]
			output_file = output_file.replace('\\', '/')
		
		self.processor_history[task_name] = {
			'last_processed' : datetime.now(timezone.utc),
			'input_files'    : set(input_files),
			'output_file'    : output_file,
		}
	
