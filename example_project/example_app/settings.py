
# Use these settings to configure Pytman for your app.
# LOG_FILE_DIR is set up for you when creating new projects. You can
# set this path to whatever you want as long as it is exists.
import os
from pathlib import Path

CHOSEN_LANGUAGE = "en-us"

# Create a new file for each time your app starts, or append the most recent one.
APPEND_LOG_FILES = True

DEFAULT_RESPONSES = {
	"en-us": {
		"NoResponse": [
			"Not sure about that one",
			"I was not expecting anything less",
			"I have no clue",
			"Your guess is as good as mine!",
			"No idea about that one",
			"I'm sorry, I don't know what you mean"
		]
	},
	"sv-se": {
		"NoResponse": [
			"Jag har inget bra svar på det faktiskt",
			"Ingen aning!",
			"Hmm... hänger inte riktigt med där",
			"Ursäkta, jag uppfattade inte?"
		]
	}
}


APP_BASE_DIR = Path(os.path.dirname(os.path.realpath(__file__)))

LOG_FILE_DIR = APP_BASE_DIR / Path("logs")

APP_NAME = "pytman-example-app"

