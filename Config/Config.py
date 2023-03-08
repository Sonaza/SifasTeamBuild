import os, sys

class Config():
	ROOT_DIRECTORY          = os.path.dirname(sys.modules['__main__'].__file__)
	
	USER_AGENT              = 'Mozilla/5.0 (compatible; sifas-cards crawler; +https://sifas-cards.sonaza.com/crawler.html) thanks for your website'
	
	OUTPUT_PUBLIC_DIRECTORY = "dist/public"
	OUTPUT_STAGE_DIRECTORY  = "dist/build-stage"
	OUTPUT_PROD_DIRECTORY   = "dist/build-prod"
	OUTPUT_LIVE_SYMLINK     = "dist/build-live"
	OUTPUT_LIVE_PATH        = "dist"
	
	TEMPLATES_DIRECTORY     = "assets/templates"
	
	RENDER_STAGE_DIRECTORY  = "build/stage"
	
	DATABASE_FILE           = "build/idols.sqlite"
	
	HISTORY_CRAWL_FILE      = "build/history_crawl.json"
	DATA_FALLBACK_FILE      = "build/data_fallback.json"
	
	ATLAS_METADATA_FILE     = "build/atlas_metadata.json"
	ATLAS_CSS_FILE          = "build/stage/atlas.css"
	
	IDOLS_CSS_FILE          = "build/stage/idols.css"
	
	RENDER_HISTORY_FILE     = "build/render_history.json"
	PROCESSOR_HISTORY_FILE  = "build/processor_history.json"
	
	BUILD_STATUS_FILE       = "build/build.status"
	
	THUMBNAILS_CACHE        = "build/thumbnails"

