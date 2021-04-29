import pytman
from features.clockfeature import ClockFeature
from features.schedulingfeature import SchedulingFeature

# These two steps are important for Pytman to work properly for your app
import settings
pytman.load_settings(settings)

# This shows a small exmaple of how you create a CommandProcessor,
# provide it with the features you want to use, then give it a spin!
processor = pytman.CommandProcessor()
processor.features = (SchedulingFeature(), ClockFeature())
message = pytman.Message()

if __name__ == "__main__":

    while 1:
        message.content = input("Write something! -> ")
        result = processor.process(message)
        print(result.response())
