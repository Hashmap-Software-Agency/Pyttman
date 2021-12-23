# Pyttman 
![Logo image](.github/cover.png)


## The Python chatbot framework with batteries included
[![PyPI version](https://badge.fury.io/py/Pyttman.svg)](https://badge.fury.io/py/Pyttman) [![CodeQL](https://github.com/dotchetter/Pyttman/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/dotchetter/Pyttman/actions/workflows/codeql-analysis.yml) [![Python package](https://github.com/dotchetter/Pyttman/actions/workflows/python-package.yml/badge.svg)](https://github.com/dotchetter/Pyttman/actions/workflows/python-package.yml)

### About
The Pyttman Framework aims to provide a similar experience as Django and Flask does for web, but for chatbots and digital assistants.

With class based intents, abilities and entities - elements which are key in any chatbot environment; they are 
offered in a very easy way to work with if one is unfamiliar with them; or a very extensive and flexible framework
with the ability to subclass and customize behavior of key parts of the framework. 

**Pyttman aims to offer developers a platform-independent experience.** 
We're constantly developing support for more platforms. As of today, Pyttman offers built-in support for Discord through the [discord.py](https://github.com/Rapptz/discord.py) library, and we have more on the way. 
All you have to do is to do is choose which platform client you use in settings.py for your app to go online 
on a different platform.

### The TL:DR

* App creation and orchestration using a built-in CLI tool: `pyttman <subcommand> <args>`
* Class-based Intents -> similar to APIView classes, to match patterns of words (rules) to your code. Ability classes wrap around Intents, which provides encapsulation and offers lifecycle hooks. 
* Built-in help generators for end-users based on metadata in your Intents
* Built-in support for Discord - more platforms to come.
* Encapsulated storage objects accessible within Intents, scoped under Ability classes
* Built-in thread based task scheduler 
* Abstraction layer middleware for managing incoming Messages just like requests in API frameworks
* Django-like settings.py file
* Powerful built-in rule-based API for parsing entities in messages (identifying words based on pre/suffixes and/or regex patterns, and/or order of appearence


### Documentation
Check out the Pyttman [Wiki](https://github.com/dotchetter/Pyttman/wiki) for documentation and tutorials. 

### Community
Join the Pyttman [Discord](https://discord.gg/s2VMAcqGzC)! We're a small but growing community of developers and enthusiasts.

### Contributions
We're looking for more contributors! Contribute with code in a PR or join our community to share ideas and thoughts.

### Open source notices
Thank you to all developers who worked on the following dependencies:

* Pyttman uses [Py7zr](https://github.com/miurahr/py7zr) for extractions 
* Pyttman uses [MultiDict](https://github.com/aio-libs/multidict) in its scheduler API 
* Pyttman uses [pytz](https://pythonhosted.org/pytz/) for timezones
* Pyttman uses [requests](https://docs.python-requests.org/en/master/) in tools offering easier API integration
* Pyttman uses [discord.py](https://github.com/Rapptz/discord.py) when adding support for native development of apps integrated with the [Discord](https://discord.com/) platform. discord.Client and discord.Message are subclassed. 

