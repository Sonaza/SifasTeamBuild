import Config
import os, sys
import inflection

class GeneratorBase:
	_imported_from_parent = set(['client', 'renderer', 'args'])
	
	def __init__(self, parent):
		self.module   = sys.modules[type(self).__module__]
		self.parent   = parent
		self.generator_file = os.path.relpath(self.module.__file__, start=Config.ROOT_DIRECTORY).replace('\\', '/')
	
	force_render   = False
	used_templates = []
	
	def render_and_save(self, *args, **kwargs):
		if 'dependencies' not in kwargs: kwargs['dependencies'] = []
		kwargs['dependencies'].append(self.generator_file)
		return self.parent.renderer.render_and_save(*args, **kwargs)
	
	def due_for_rendering(self):
		return self.force_render or any([self.parent.due_for_rendering(template) for template in self.used_templates])
	
	def generate_and_render(self):
		raise NotImplementedError()
	
	def __getattr__(self, attr):
		if attr == "generator_display_name":
			generator_name = inflection.underscore(type(self).__name__)
			generator_name = inflection.humanize(generator_name)
			generator_name = inflection.titleize(generator_name)
			return generator_name
		
		if attr in self._imported_from_parent:
			return getattr(self.parent, attr)
		
		if attr.endswith('_generator'):
			generator_name = inflection.camelize(attr)
			try:
				return self.parent.generators[generator_name]
			except KeyError:
				raise NameError(f"{generator_name} not found or initialised.")
 		
		return GeneratorBase.__getattribute__(self, attr)
