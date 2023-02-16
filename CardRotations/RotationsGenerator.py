import Config
from IdolDatabase import *

from . import ResourceProcessor, PageRenderer, CardThumbnails, CardValidity
from .Utility import Utility

import os
import sys
import platform
import argparse

from colorama import init as colorama_init, Fore, Style

from io import StringIO
class stdout_wrapper(StringIO):
	global_indent = 0
	def __init__(self):
		self.old_stdout = sys.stdout
		self.need_indent = True
		
	def write(self, string):
		parts = re.split('(.*\n)', string)
		for part in parts:
			if not part: continue
			
			if self.need_indent:
				self.old_stdout.write(' ' * stdout_wrapper.global_indent)
				
			self.old_stdout.write(part)
			self.need_indent = (part[-1] == '\n')
				
	def flush(self):
		self.old_stdout.flush()
		

class print_indent():
	def __init__(self, indent = 0):
		self.indent = indent
		
	def __enter__(self):
		stdout_wrapper.global_indent += self.indent
		return self
		
	def __exit__(self, type, value, traceback):
		stdout_wrapper.global_indent -= self.indent
		stdout_wrapper.global_indent = max(0, stdout_wrapper.global_indent)
		
	@staticmethod
	def add(indent):
		stdout_wrapper.global_indent += indent

	@staticmethod
	def reduce(indent):
		stdout_wrapper.global_indent -= indent
		stdout_wrapper.global_indent = max(0, stdout_wrapper.global_indent)

import builtins
builtins.print_indent = print_indent

class RotationsGenerator:
	
	def __init__(self):
		self.parser = argparse.ArgumentParser(description='Make some card rotations.')
		
		self.parser.add_argument("-f", "--force", "--force-build",
							help="Force database update regardless of when it was last performed and then force renders everything.",
							action="store_true")
		
		self.parser.add_argument("-fr", "--force-render",
							help="Force render of all templates regardless if they've changed (database update not forced).",
							action="store_true")
		
		self.parser.add_argument("-ra", "--remake-atlas",
							help="Remake the thumbnail atlas planes and the associated CSS code.",
							action="store_true")
		
		self.parser.add_argument("-hf", "--history-from-file",
							help="Loads history from file instead of doing a crawl. Reduces the load on Kirara.",
							action="store_true")
		
		self.parser.add_argument('--rescrape',
							help="Rescrape data for idols released in the past this many days. Default: 14",
							action="store", metavar='DAYS', type=int, default=14)
		
		self.parser.add_argument("--auto", help="Flags this update as having been done automatically.",
							action="store_true")
		
		self.parser.add_argument("--dev", help="Flags it as developing build.",
							action="store_true")
		
		self.parser.add_argument("-w", "--watch",
							help="Instead of generating pages, start watching for asset changes and reprocessing them when modified.",
							action="store_true")
		
		self.parser.add_argument("--colored-output", help=argparse.SUPPRESS,
							action="store_true", default=True)
		
		self.parser.add_argument("--no-colored-output", help="Disables log colors. Colors are enabled by default.",
							action="store_false", dest='colored_output')
		
		self.args = self.parser.parse_args()
		
		# Only strip on windows for Sublime Text, somehow it still displays in console?
		colorama_init(autoreset=True, strip=not self.args.colored_output)
		
		sys.stdout = stdout_wrapper()
		
		self.resource_processor_settings = dotdict(
		{
			'js' : dotdict({
				'processor'        : ResourceProcessor.JavascriptResourceProcessor,
				'watch_directory'  : "assets/",
				'watched_files'    : [
					"assets/js/*.js",
					"assets/js/*/*.js",
				],
				'input_files'      : [
					"assets/js/build_id.js",
					"assets/js/AppModule.js",
					"assets/js/Constants.js",
					"assets/js/Enums.js",
					"assets/js/Utility.js",
					"assets/js/CardTooltip.js",
					"assets/js/providers/*.js",
					"assets/js/factories/*.js",
					"assets/js/directives/*.js",
					"assets/js/controllers/*.js",
					"assets/js/AppConfig.js",
					"assets/js/TooltipsCache.js",
				],
				'output_file'      : os.path.join(Config.OUTPUT_DIRECTORY, "js/public.min.js").replace('\\', '/'),
				'depends'          : ['tooltip'],
			}),
			
			'css' : dotdict({
				'processor'        : ResourceProcessor.CSSResourceProcessor,
				'watch_directory'  : "assets/",
				'watched_files'    : [
					"assets/css/*.css",
					"assets/css/*.scss",
				],
				'input_files'      : [
					"public/css/fonts.css",
					"assets/css/atlas.css",
					"assets/css/idols.css",
					"assets/css/style.scss",
					"assets/css/style-scrollbar.scss",
					"assets/css/style-timeline.scss",
					"assets/css/style-darkmode.scss",
					"assets/css/style-mobile.scss",
					"assets/css/style-timeline-mobile.scss",
					"assets/css/style-darkmode-mobile.scss",
				],
				'output_file'      : os.path.join(Config.OUTPUT_DIRECTORY, "css/public.min.css").replace('\\', '/'),
			}),
			
			'tooltip' : dotdict({
				'processor'        : ResourceProcessor.TooltipsResourceProcessor,
				'watch_directory'  : "assets/",
				'watched_files'    : [
					"assets/tooltips/*.html",
				],
				'input_files'      : [
					"assets/tooltips/*.html",
				],
				'output_file'      : "assets/js/TooltipsCache.js",
			}),
		})
	
	def initialise_generators(self):
		self.generators = {}
		#    BasicRotationsGenerator        ... OK
		#Unchanged  home.html                      ...  OK
		print()
		print("Loading generators...")
		from .Generators import Generators
		for generator_name, generator_module in Generators.items():
			self.generators[generator_name] = getattr(generator_module, generator_name)(self)
			# print(f"  {self.generators[generator_name].generator_name:<39} ...  OK")
		print()
	
	def initialize(self):
		self.processor = ResourceProcessor.ResourceProcessor(self, self.resource_processor_settings)
		if self.args.watch:
			self.processor.watch_changes()
			exit()
			
		if not os.path.exists("assets/css/idols.css"):
			raise Exception("Generated idols.css does not exist! Run tools/generate_idols_css.py")
		
		if self.args.dev:
			print("------ BUILDING IN DEV MODE ------")
		else:
			print("------ BUILDING IN PROD MODE ------")
		
		print(f"  Python version    : {platform.python_version()}")
		print()
		print(f"  Forced Update     : {self.args.force}")
		print(f"  Forced Rendering  : {self.args.force_render}")
		print(f"  Atlas Remake      : {self.args.remake_atlas}")
		
		try:
			print("  Current UID       :", os.getuid())
		except:
			pass
		print( "  Working Directory :", os.getcwd())
		print()
		
		self.client = KiraraClient(database_file=Config.DATABASE_FILE)
		try:
			self.client.update_database(
				forced_update          = self.args.force,
				load_history_from_file = self.args.history_from_file,
				rescrape_days          = self.args.rescrape)
		except KiraraClientException as e:
			print("Database update failed: ", e)
			print()
		
		self.renderer = PageRenderer.PageRenderer(self)
		if not self.renderer.is_render_history_loaded():
			print("Render history load failed, a full render is required!")
			self.args.force_render = True
			
		if not os.path.exists("public/js/tooltip_data.js"):
			print("Tooltip data file does not exist, a full render is required!")
			self.args.force_render = True
		
		if not os.path.exists("assets/css/atlas.css"):
			print("Atlas CSS does not exist and must be regenerated!")
			self.args.remake_atlas = True
		
		self.thumbnails = CardThumbnails.CardThumbnails(self.client)
		if not self.thumbnails.metadata_loaded_successfully():
			print("Atlas metadata does not exist or is corrupted and must be regenerated!")
			self.args.remake_atlas = True
		
		if self.thumbnails.download_thumbnails() or self.args.remake_atlas:
			self.thumbnails.make_atlas()
			self.args.force_render = True
		
		self.initialise_generators()
	
	# -------------------------------------------------------------------------------------------
	
	def get_preload_assets(self):
		preload_assets = []
		preload_asset_files = Utility.glob([
			self.resource_processor_settings.css.output_file,
			os.path.join(Config.OUTPUT_DIRECTORY, "js/vendor/angular/angular-combined.min.js"),
			os.path.join(Config.OUTPUT_DIRECTORY, "js/public.min.js"),
			os.path.join(Config.OUTPUT_DIRECTORY, "js/tooltip_data.js"),
			os.path.join(Config.OUTPUT_DIRECTORY, "img/thumbnails/atlas_*_30_*_idolized.webp")
		])
		
		ext_types = {
			'.css'  : 'style',
			'.gif'  : 'image',
			'.png'  : 'image',
			'.webp' : 'image',
			'.jpg'  : 'image',
			'.jpeg' : 'image',
			'.js'   : 'script',
		}
		
		for filepath in preload_asset_files:
			rel = 'preload'
			
			filepath = filepath.replace('\\', '/')
			filehash = Utility.get_file_modifyhash(filepath)
			
			relative_path = filepath.replace('public/', '')
			base, ext = os.path.splitext(relative_path)
			
			preload_assets.append({
				'path'   : f"/{base}.{filehash}{ext}",
				'type'   : ext_types[ext],
				'rel'    : rel,
			})
			
		return preload_assets
	
	# --------------------------------------------
	
	def is_doing_full_render(self):
		return self.args.force or self.args.force_render or self.client.database_updated()
	
	def due_for_rendering(self, template_filename):
		if self.is_doing_full_render():
			return True
		return self.renderer.due_for_rendering(template_filename)
		
	def run_generators(self):
		for generator_name, generator in self.generators.items():
			print(f"──────── {generator.generator_display_name + ' ':─<110}")
			print()
			with print_indent(4):
				if generator.due_for_rendering():
					generator.generate_and_render()
			print()
			
	def generate_pages(self):
		files_to_delete = Utility.glob([
			os.path.join(Config.OUTPUT_DIRECTORY, "pages/*.html"),
			os.path.join(Config.OUTPUT_DIRECTORY, "pages/*/*.html")
		])
		
		render_start_time = time.perf_counter()
		
		# If we're doing full render anyway there's no need to keep old history.
		# Clearing it just in case some crud accumulates there too.
		if self.is_doing_full_render():
			self.renderer.reset_render_history()
		
		# -------------------------------------------------------
		# Build ID
		
		random_build_id = str(hex(hash(time.time())))[2:8]
		self.renderer.render_and_save("build_id_template.js", "../assets/js/build_id.js",
		{
			'build_id' : random_build_id,
		}, minify=not self.args.dev)
		print()
		
		# -------------------------------------------------------
		# Page Generators
		
		self.run_generators()
		
		# -------------------------------------------------------
		# Index page
		
		if self.due_for_rendering("home.html"):
			self.renderer.render_and_save("home.html", "pages/home.html", {}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Save tooltip data cache
		# Must be after all card pages have been rendered but before preloads!
		
		if self.is_doing_full_render():
			self.renderer.save_tooltip_data("js/tooltip_data.js")
			
		# -------------------------------------------------------
		# Process Javascript and CSS
		
		self.processor.process_all_resources(
			force  = self.is_doing_full_render() or not self.processor.processor_history_loaded_successfully(),
			minify = not self.args.dev)
		
		# -------------------------------------------------------
		# Error Pages
		
		if self.due_for_rendering("error.html"):
			self.renderer.render_and_save("error.html", "error/400.html", {
				'error_code'   : 400,
				'error_status' : 'Bad Request',
				'error_text'   : "The server is unable to handle the malformed request made by your browser.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/403.html", {
				'error_code'   : 403,
				'error_status' : 'Forbidden',
				'error_text'   : "You are not permitted to access this resource. Move along, citizen.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/404.html", {
				'error_code'   : 404,
				'error_status' : 'Not Found',
				'error_text'   : "Whoopsie! Whatever it is you're looking for at this URL does not exist.<br><br>If a page links here directly or you think something should have been here please send feedback.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/410.html", {
				'error_code'   : 410,
				'error_status' : 'Gone',
				'error_text'   : "Whoopsie! Whatever it is you're looking for at this URL is permanently gone.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/500.html", {
				'error_code'   : 500,
				'error_status' : 'Server Error',
				'error_text'   : "The server encountered an unrecoverable error while processing your request.<br><br>Please try again later.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/503.html", {
				'error_code'   : 503,
				'error_status' : 'Unavailable',
				'error_text'   : "Service is temporarily unavailable. Please try again later.",
			}, minify=True)
		
		# -------------------------------------------------------
		# Crawler Info
		
		if self.due_for_rendering("crawler.html"):
			self.renderer.render_and_save("crawler.html", "crawler.html", {}, minify=True)
		
		# -------------------------------------------------------
		# .htaccess
		
		preload_assets = self.get_preload_assets()
		self.renderer.render_and_save("template.htaccess", ".htaccess", {
			'preloads' : preload_assets
		}, minify=False, generated_note=True)
		
		# -------------------------------------------------------
		# Main index and layout
		
		render_time_so_far = time.perf_counter() - render_start_time
		
		last_data_update = self.client.get_database_update_time()
		now = datetime.now(timezone.utc)
		self.renderer.render_and_save("main_layout.php", "views/content_index.php", {
			'last_update'      : now,
			'last_data_update' : last_data_update,
			'render_time'      : f"{render_time_so_far:0.2f}s",
			'preloads'         : preload_assets,
		}, minify=False, output_basepath='')
		
		# -------------------------------------------------------
		# File cleanup
		
		self.renderer.save_render_history()
		
		for file in files_to_delete:
			if file in self.renderer.rendered_pages: continue
			
			print(f"Removing outdated file  {file}")
			os.remove(file)
		
		render_time_total = time.perf_counter() - render_start_time
		print(f"\nAll done! Rendering took {render_time_total:0.3f}s\n")
