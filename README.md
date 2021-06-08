# Pyttman 
![Logo image](.github/cover.png)
# The virtual assistant framework made for developers with ideas

Pyttman is a framework for developing virtual assistants, chatbots or other language driven applications.
It houses base classes and ready-to-use classes, both for making powerful custom features, or using the 
ones already provided for you, as pluggable objects.

It is inspired by [Django](https://www.djangoproject.com), and aspires to offer a similar ease of use as Django does for web, but
for chatbots and personal digital assistants.


## What is Pyttman?

Pyttman is a high level framework which abstracts away much of the hard work when developing natural-language-command-driven apps. 

#### A few bullet points are:

* No more tangled if-statements for deciphering a user command based on certain words. 
* 100% object-oriented with base classes for subclassing as an alternative to using the presets.
* A clear and consice structure for how your app can be built and scale, with a directory structure set up for you.
* Offers a familiar syntax for developers with previous experience in [Django](https://www.djangoproject.com)
* Easy to use for simple projects - powerful and flexible for more complex projects
* Contains logging, scheduling and built-in client support for major platforms


## Get started

It's very easy to get started with Pyttman. 

1. Install it using pip: `pip install pyttman`
2. Navigate to the directory where you want to develop your Pyttman app
3. Start a project using the command `pyttman-cli newapp <app_name>`
4. You now have a template Pyttman app. Run it with the shell client using `pyttman-cli dev <app_name>`.
   To use the included ClockFeature for demo purposes, import it in `settings.py` and update `FEATURES` to `FEATURES = [ClockFeature()]`
5. Add settings to `settings.py` as you wish and access them in your app through `pyttman.settings.setting_name`
6. Consult the documentation for guidance on how to use Pyttman to its full potential by integrating your app with a chat service or your own website.


### Contributions

Contributions are more than welcome - write your PR in a branch named 'contribution-<my_contrib>' ideally.


### Open source notices
On behalf of the Pyttman dev team, thank you to all developers who worked on the following dependencies:

* Pyttman uses [Py7zr](https://github.com/miurahr/py7zr) for extractions 
* Pyttman uses [MultiDict](https://github.com/aio-libs/multidict) in its scheduler API 
* Pyttman uses [pytz](https://pythonhosted.org/pytz/) for timezones
* Pyttman uses [requests](https://docs.python-requests.org/en/master/) in tools offering easier API integration




