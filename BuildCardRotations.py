import Config
import CardRotations
from datetime import datetime, timezone

import json

if __name__ == "__main__":
	cr = CardRotations.RotationsGenerator()
	
	buildstatus = {
		"timestamp" : datetime.now(timezone.utc).isoformat(),
		"handled"   : None,
		"auto"      : cr.args.auto,
		"forced"    : cr.args.force,
		"success"   : None,
		"message"   : "",
	}
	build_exception = None
	
	cr.initialize()
	
	try:
		cr.generate_pages()
		buildstatus['success'] = True
		buildstatus['message'] = "All OK!"
		
	except Exception as e:
		buildstatus['success'] = False
		
		import traceback
		buildstatus['message'] = traceback.format_exc()
		
		build_exception = e
	
	with open(Config.BUILD_STATUS_FILE, "w", encoding="utf-8") as output_file:
		json.dump(buildstatus, output_file)
	
	if not buildstatus['success']:
		raise build_exception
	
	print()
