import pyttman
import pyttman.core.communication.command
import pyttman.core.communication.models.containers
from features.clockfeature import ClockFeature
from pyttman.core.parsing.routing import LinearSearchFirstMatchingRouter

# These two steps are important for Pyttman to work properly for your app
import settings
pyttman.load_settings(settings)

# This shows a small exmaple of how you create a CommandProcessor,
# provide it with the features you want to use, then give it a spin!
processor = pyttman.CommandProcessor()
message = pyttman.core.communication.models.containers.Message()

if __name__ == "__main__":
    router = LinearSearchFirstMatchingRouter()
    router.features = (ClockFeature(),)
    while 1:
        message.content = input("Write something! -> ")
        result = router.get_reply(message)
        print(result.as_str())
