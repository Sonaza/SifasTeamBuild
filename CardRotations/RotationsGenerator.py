import Config
from IdolDatabase import *

import ResourceProcessor
# from ResourceProcessor.FileProcessors import *

from . import PageRenderer, CardThumbnails, CardValidity
from Common import Utility

import os
import sys
import shutil
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
		
		self.parser.add_argument("--watch",
							help="Instead of generating pages, start watching for asset changes and reprocessing them when modified.",
							action="store_true")
		
		self.parser.add_argument("--watch-polling",
							help="Same as --watch but uses polling observer instead. Use when you can't rely on inotify events.",
							action="store_true")
		
		self.parser.add_argument("--kill-duplicates", help=argparse.SUPPRESS,
							action="store_true", default=True)
		
		self.parser.add_argument("--no-kill-duplicates", help="By default when watcher is started duplicate watcher processes are killed. Use this to disable.",
							action="store_false", dest='kill_duplicates')
		
		self.parser.add_argument("--colored-output", help=argparse.SUPPRESS,
							action="store_true", default=True)
		
		self.parser.add_argument("--no-colored-output", help="Disables log colors. Colors are enabled by default.",
							action="store_false", dest='colored_output')
		
		self.args = self.parser.parse_args()
		
		# Only strip on windows for Sublime Text, somehow it still displays in console?
		colorama_init(autoreset=True, strip=not self.args.colored_output)		
		sys.stdout = stdout_wrapper()
		
		self.resource_processor_tasks = [
			# ResourceProcessor.ProcessorTask(
			# 	name             = 'CommandTest',
			# 	post_command     = ['echo', '"hello world"'],
			# 	watch_directory  = "assets/",
			# 	watched_files    = [
			# 		"assets/js/*.js",
			# 		"assets/js/*/*.js",
			# 	],
			# 	depends_on       = [],
			# ),
			
			ResourceProcessor.ProcessorTask(
				name             = 'JavaScript',
				file_processor   = ResourceProcessor.FileProcessors.JavascriptFileProcessor,
				watch_directory  = "assets/",
				watched_files    = [
					"assets/js/**/*.js",
				],
				input_files      = [
					os.path.join(Config.RENDER_STAGE_DIRECTORY, "build_id.js"),
					"assets/js/AppModule.js",
					"assets/js/Constants.js",
					"assets/js/classes/*.js",
					"assets/js/providers/*.js",
					"assets/js/factories/*.js",
					"assets/js/directives/*.js",
					"assets/js/controllers/*.js",
					"assets/js/AppConfig.js",
					os.path.join(Config.RENDER_STAGE_DIRECTORY, "TemplateCache.js"),
				],
				output_file      = os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "js/public.min.js"),
				depends_on       = ['TemplateCache'],
			),
			
			ResourceProcessor.ProcessorTask(
				name             = 'CSS',
				file_processor   = ResourceProcessor.FileProcessors.CSSFileProcessor,
				watch_directory  = "assets/",
				watched_files    = [
					"assets/css/**/*.css",
					"assets/css/**/*.scss",
				],
				input_files      = [
					Config.ATLAS_CSS_FILE,
					Config.IDOLS_CSS_FILE,
					"assets/css/fonts.css",
					"assets/css/style.scss",
					"assets/css/style-scrollbar.scss",
					"assets/css/style-timeline.scss",
					"assets/css/style-darkmode.scss",
					"assets/css/style-mobile.scss",
					"assets/css/style-timeline-mobile.scss",
					"assets/css/style-darkmode-mobile.scss",
					"assets/css/components/*.scss",
				],
				output_file      = os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "css/public.min.css"),
			),
			
			ResourceProcessor.ProcessorTask(
				name             = 'TemplateCache',
				file_processor   = ResourceProcessor.FileProcessors.TemplateCacheFileProcessor,
				watch_directory  = "assets/",
				watched_files    = [
					"assets/templatecache/*.html",
				],
				input_files      = [
					os.path.join(Config.RENDER_STAGE_DIRECTORY, "member_select_box.html"),
					"assets/templatecache/*.html",
				],
				output_file      = os.path.join(Config.RENDER_STAGE_DIRECTORY, "TemplateCache.js"),
			),
		]
	
	def initialise_generators(self):
		self.generators = {}
		print()
		print("Loading generators...")
		from .Generators import Generators
		for generator_name, generator_module in Generators.items():
			self.generators[generator_name] = getattr(generator_module, generator_name)(self)
		print()
	
	def initialize(self):
		self.processor = ResourceProcessor.ResourceProcessor(self, self.resource_processor_tasks)
		
		if self.args.watch or self.args.watch_polling:
			self.processor.watch_changes(
				kill_duplicates = self.args.kill_duplicates,
				polling         = self.args.watch_polling)
			exit()
		
		if not os.path.exists(Config.IDOLS_CSS_FILE):
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
			
		tooltip_path = os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "js/tooltip_data.js")
		if not os.path.exists(tooltip_path):
			print("Tooltip data file does not exist, a full render is required!")
			self.args.force_render = True
		
		self.thumbnails = CardThumbnails.CardThumbnails(self.client)
		if self.thumbnails.reprocessing_required():
			self.args.remake_atlas = True
		
		if self.thumbnails.download_thumbnails() or self.args.remake_atlas:
			self.thumbnails.make_atlas()
			self.args.force_render = True
		
		self.initialise_generators()
	
	# -------------------------------------------------------------------------------------------
	
	def get_preload_assets(self):
		preload_assets = []
		preload_asset_files = Utility.glob([
			os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "css/public.min.css"),
			os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "js/vendor/angular/angular-combined.min.js"),
			os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "js/public.min.js"),
			os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "js/tooltip_data.js"),
			os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "thumbnails/atlas_*_30_*_idolized.webp")
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
			filehash = Utility.get_file_modify_hash(filepath)
			
			relative_path = filepath.replace(Config.OUTPUT_STAGE_DIRECTORY, Config.OUTPUT_LIVE_PATH)
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
			print(f"──────── {generator.generator_display_name + ' ':─<70}")
			print()
			with print_indent(4):
				if generator.due_for_rendering():
					generator.generate_and_render()
			print()
			
	def generate_pages(self):
		files_to_delete = Utility.glob([
			os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "pages/*.html"),
			os.path.join(Config.OUTPUT_STAGE_DIRECTORY, "pages/*/*.html")
		])
		
		render_start_time = time.perf_counter()
		
		# If we're doing full render anyway there's no need to keep old history.
		# Clearing it just in case some crud accumulates there too.
		if self.is_doing_full_render():
			self.renderer.reset_render_history()
		
		# -------------------------------------------------------
		# Build ID
		
		random_build_id = str(hex(hash(time.time())))[2:8]
		self.renderer.render_and_save("build_id_template.js", "build_id.js",
		{
			'build_id' : random_build_id,
		}, output_basepath=Config.RENDER_STAGE_DIRECTORY)
		print()
		
		# -------------------------------------------------------
		# Page Generators
		
		self.run_generators()
		
		# -------------------------------------------------------
		# Miscellaneous
		
		if self.due_for_rendering("member_select_box.html"):
			self.renderer.render_and_save("member_select_box.html", "member_select_box.html", {},
				minify_html=False, output_basepath=Config.RENDER_STAGE_DIRECTORY)
		
		# -------------------------------------------------------
		# Index page
		
		if self.due_for_rendering("home.html"):
			self.renderer.render_and_save("home.html", "pages/home.html", {}, minify_html=not self.args.dev)
		
		# -------------------------------------------------------
		# Save tooltip data cache
		# Must be after all card pages have been rendered but before preloads!
		
		if self.is_doing_full_render():
			self.renderer.save_tooltip_data("js/tooltip_data.js")
			
		# -------------------------------------------------------
		# Process Javascript and CSS
		
		self.processor.process_all_resources(
			force  = self.is_doing_full_render(),
			minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Error Pages
		
		if self.due_for_rendering("error.html"):
			self.renderer.render_and_save("error.html", "error/400.html", {
				'error_code'   : 400,
				'error_status' : 'Bad Request',
				'error_text'   : "The server is unable to handle the malformed request made by your browser.",
			}, minify_html=True)
			
			self.renderer.render_and_save("error.html", "error/403.html", {
				'error_code'   : 403,
				'error_status' : 'Forbidden',
				'error_text'   : "You are not permitted to access this resource. Move along, citizen.",
			}, minify_html=True)
			
			self.renderer.render_and_save("error.html", "error/404.html", {
				'error_code'   : 404,
				'error_status' : 'Not Found',
				'error_text'   : "Whoopsie! Whatever it is you're looking for at this URL does not exist.<br><br>If a page links here directly or you think something should have been here please send feedback.",
			}, minify_html=True)
			
			self.renderer.render_and_save("error.html", "error/410.html", {
				'error_code'   : 410,
				'error_status' : 'Gone',
				'error_text'   : "Whoopsie! Whatever it is you're looking for at this URL is permanently gone.",
			}, minify_html=True)
			
			self.renderer.render_and_save("error.html", "error/500.html", {
				'error_code'   : 500,
				'error_status' : 'Server Error',
				'error_text'   : "The server encountered an unrecoverable error while processing your request.<br><br>Please try again later.",
			}, minify_html=True)
			
			self.renderer.render_and_save("error.html", "error/503.html", {
				'error_code'   : 503,
				'error_status' : 'Unavailable',
				'error_text'   : "Service is temporarily unavailable. Please try again later.",
			}, minify_html=True)
		
		# -------------------------------------------------------
		# Crawler Info
		
		if self.due_for_rendering("crawler.html"):
			self.renderer.render_and_save("crawler.html", "pages/crawler.html", {}, minify_html=True)
		
		# -------------------------------------------------------
		# .htaccess
		
		preload_assets = self.get_preload_assets()
		self.renderer.render_and_save("template.htaccess", ".htaccess", {
			'preloads' : preload_assets
		}, generated_note=True)
		
		# -------------------------------------------------------
		# Main index and layout
		
		render_time_so_far = time.perf_counter() - render_start_time
		
		last_data_update = self.client.get_database_update_time()
		now = datetime.now(timezone.utc)
		self.renderer.render_and_save("main_layout.php", "main_index.php", {
			'last_update'      : now,
			'last_data_update' : last_data_update,
			'render_time'      : f"{render_time_so_far:0.2f}s",
			'preloads'         : preload_assets,
		}, minify_html=False, output_basepath='dist/views/')
		
		# -------------------------------------------------------
		# File cleanup
		
		self.renderer.save_render_history()
		
		for file in files_to_delete:
			if file in self.renderer.rendered_pages: continue
			
			print(f"Removing outdated file  {file}")
			os.remove(file)
		
		# -------------------------------------------------------
		# Symlinking
		
		symlink_success = self.create_symlinks()
		if symlink_success:
			print("Copying .htaccess to public root...")
			shutil.copy(os.path.join(Config.OUTPUT_STAGE_DIRECTORY, ".htaccess"), os.path.join(Config.OUTPUT_PUBLIC_DIRECTORY, ".htaccess"))
		else:
			print("Symlinking failed, build is not live!")
		
		render_time_total = time.perf_counter() - render_start_time
		print(f"\nAll done! Rendering took {render_time_total:0.3f}s\n")
	
	
	def create_symlinks(self):
		print()
		print(f"{Fore.BLUE}{Style.BRIGHT}Creating symlinks...")
		
		if self.args.dev:
			return self.create_dev_symlinks()
		else:
			return self.create_prod_symlinks()
	
	
	def create_dev_symlinks(self):
		try:
			current_symlink = os.readlink(Config.OUTPUT_LIVE_SYMLINK)
		except FileNotFoundError:
			current_symlink = None
		
		if current_symlink == os.path.basename(Config.OUTPUT_STAGE_DIRECTORY):
			# print(f"  {Fore.GREEN}{Style.BRIGHT}Current dev build symlink is OK.")
			return True
			
		try: 
			print(f"  {Fore.YELLOW}{Style.BRIGHT}Current dev build symlink does not point to {Fore.WHITE}{Config.OUTPUT_STAGE_DIRECTORY}   {Fore.GREEN}Updating symlink...")
			if os.path.exists(Config.OUTPUT_LIVE_SYMLINK):
				os.remove(Config.OUTPUT_LIVE_SYMLINK)
			os.symlink(os.path.basename(Config.OUTPUT_STAGE_DIRECTORY), Config.OUTPUT_LIVE_SYMLINK)
		except:
			print("Failed to create symlink!")
			return False
			
		return True
		
	def create_prod_symlinks(self):
		old_prod_directories = Utility.glob([Config.OUTPUT_PROD_DIRECTORY + '*'])
		
		prod_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
		prod_symlink_target = f"{Config.OUTPUT_PROD_DIRECTORY}-{prod_timestamp}"
		
		print(f"  {Fore.YELLOW}{Style.BRIGHT}Updating production build symlink to {Fore.WHITE}{prod_symlink_target}  ...  ", end='')
		
		from distutils.dir_util import copy_tree, remove_tree
		copy_tree(Config.OUTPUT_STAGE_DIRECTORY, prod_symlink_target)
		
		try: 
			if os.path.exists(Config.OUTPUT_LIVE_SYMLINK):
				os.remove(Config.OUTPUT_LIVE_SYMLINK)
			os.symlink(os.path.basename(prod_symlink_target), Config.OUTPUT_LIVE_SYMLINK, target_is_directory=True)
			print("OK!")
			
		except:
			print("Failed to create symlink!")
			return False
		
		for old_dirpath in old_prod_directories:
			print("  Removing old build-prod directory: ", old_dirpath)
			remove_tree(old_dirpath)
		
		return True
