schemas = [
	# ------------------------------------------------------------------
	# Database Tables
	# ------------------------------------------------------------------
	
	# Database params
	'''CREATE TABLE `parameters` (
		`key`         TEXT UNIQUE NOT NULL,
		`value`       TEXT,
	    PRIMARY KEY(`key`)
	) WITHOUT ROWID''',
	
	# Idols json table
	'''CREATE TABLE `idols_json` (
	    `ordinal`           INTEGER UNIQUE,
	    `json`              TEXT,
	    PRIMARY KEY(`ordinal`)
	) WITHOUT ROWID''',
	
	# Attributes table
	'''CREATE TABLE `attributes` (
	    `id`                INTEGER UNIQUE NOT NULL,
	    `name`              TEXT,
	    PRIMARY KEY(`id`)
	) WITHOUT ROWID''',
	
	# Types table
	'''CREATE TABLE `types` (
	    `id`                INTEGER UNIQUE NOT NULL,
	    `name`              TEXT,
	    `full_name`         TEXT,
	    PRIMARY KEY(`id`)
	) WITHOUT ROWID''',
	
	# Groups table
	'''CREATE TABLE `groups` (
	    `id`                INTEGER UNIQUE NOT NULL,
	    `tag`               TEXT,
	    `name`              TEXT,
	    PRIMARY KEY(`id`)
	) WITHOUT ROWID''',
	
	# Subunit table
	'''CREATE TABLE `subunits` (
	    `id`                INTEGER UNIQUE NOT NULL,
	    `name`              TEXT,
	    PRIMARY KEY(`id`)
	) WITHOUT ROWID''',
	
	# Members table
	'''CREATE TABLE `members` (
	    `id`                INTEGER UNIQUE NOT NULL,
	    `name`              TEXT,
	    `year`              INTEGER,
	    `group_id`          INTEGER NOT NULL,
	    `subunit_id`        INTEGER NOT NULL,
	    FOREIGN KEY(`group_id`)     REFERENCES groups(`id`),
	    FOREIGN KEY(`subunit_id`)   REFERENCES subunits(`id`),
	    PRIMARY KEY(`id`)
	) WITHOUT ROWID''',
	
	# Idols table
	'''CREATE TABLE `idols` (
	    `ordinal`           INTEGER UNIQUE NOT NULL,
	    `id`                INTEGER UNIQUE NOT NULL,
	    `member_id`         INTEGER,
--	    `group_id`          INTEGER,
--	    `subunit_id`        INTEGER,
	    `normal_name`       TEXT,
	    `idolized_name`     TEXT,
	    `attribute`         INTEGER,
	    `type`              INTEGER,
	    `rarity`            INTEGER,
	    `source`            INTEGER,
	    `release_date`      TEXT,
	    FOREIGN KEY(`member_id`)    REFERENCES members(`id`),
--	    FOREIGN KEY(`group_id`)     REFERENCES groups(`id`),
--	    FOREIGN KEY(`subunit_id`)   REFERENCES subunits(`id`),
	    FOREIGN KEY(`attribute`)    REFERENCES attributes(`id`),
	    FOREIGN KEY(`type`)         REFERENCES types(`id`),
	    PRIMARY KEY(`ordinal`, `id`)
	) WITHOUT ROWID''',
	
	# Events table
	'''CREATE TABLE `events` (
		`id`                INTEGER UNIQUE NOT NULL,
	    `type`              INTEGER,
	    `title_en`          TEXT UNIQUE,
	    `start_en`          TEXT,
	    `end_en`            TEXT,
	    `title_jp`          TEXT UNIQUE,
	    `start_jp`          TEXT,
	    `end_jp`            TEXT,
	    PRIMARY KEY(`id` AUTOINCREMENT)
	)''',
	
	# Events related cards
	'''CREATE TABLE `event_cards` (
	    `event_id`          INTEGER NOT NULL,
	    `ordinal`           INTEGER NOT NULL,
	    CONSTRAINT `event_id_ordinal` UNIQUE(`event_id`, `ordinal`),
	    FOREIGN KEY(`event_id`)     REFERENCES events(`id`)      ON DELETE CASCADE,
	    FOREIGN KEY(`ordinal`)      REFERENCES idols(`ordinal`),
	    PRIMARY KEY(`event_id`, `ordinal`)
	)''',
	
	# Passive skills
	# '''CREATE TABLE `skills` (
	# 	`skill_id`            INTEGER PRIMARY KEY,
	# 	`name`                TEXT,
	# 	`description`         TEXT,
	# 	`trigger_type`        INTEGER,
	# 	`trigger_probability` INTEGER,
	# 	`effect_type`         INTEGER,
	# 	`target`              INTEGER,
	# 	`levels`              TEXT,
	# ) WITHOUT ROWID''',
	
	# Idols skills table
	# '''CREATE TABLE `idols_skills` (
	#     `ordinal`           INTEGER UNIQUE,
	#     `primary_passive`   INTEGER,
	#     `secondary_passive` INTEGER,
	#     PRIMARY KEY(`ordinal`),
	#     FOREIGN KEY(`primary_passive`)   REFERENCES skills(`id`),
	#     FOREIGN KEY(`secondary_passive`) REFERENCES skills(`id`)
	# ) WITHOUT ROWID''',
	
	# ------------------------------------------------------------------
	# Database Views
	# ------------------------------------------------------------------
	
	'''CREATE VIEW v_idols AS
	    SELECT
	        idols.*,
	        members.group_id,
	        members.subunit_id,
	        members.year
	    FROM idols
	    INNER JOIN members    ON idols.member_id = members.id
	''',
	
	'''CREATE VIEW v_idols_with_events AS
	    SELECT
	        v_idols.*,
	        events.title_en AS event_title
	    FROM v_idols
	    LEFT JOIN event_cards ON event_cards.ordinal = v_idols.ordinal
	    LEFT JOIN events      ON events.id = event_cards.event_id
	''',
	
]
