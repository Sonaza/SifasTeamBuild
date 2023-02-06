import os

class Config():
	USER_AGENT          = 'Mozilla/5.0 (compatible; sifas-cards crawler; +https://sifas-cards.sonaza.com/crawler.html) thanks for your website'
	
	DATABASE_FILE       = "build/idols.sqlite"
	
	HISTORY_CRAWL_FILE  = "build/history_crawl.json"
	DATA_FALLBACK_FILE  = "build/data_fallback.json"
	
	ATLAS_METADATA_FILE = "build/atlas_metadata.json"
	RENDER_HISTORY_FILE = "build/render_history.json"
	
	BUILD_STATUS_FILE   = "build/build.status"
