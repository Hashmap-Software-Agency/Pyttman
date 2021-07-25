# Pyttman 
![Logo image](.github/cover.png)
## The digital assistant framework made for developers with ideas

Pyttman is a framework for developing digital assistants, chatbots or other language driven applications.

It is inspired by [Django](https://www.djangoproject.com) in a few design aspects and the developer experience, and aspires to offer a similar ease of use but for chatbots / digital assistants.


> *My goal with Pyttman is to enable developers as little friction and complexity as possible when they set out to develop chat bots, digital assistants or otherwise natural-languate-powered apps.* 
>
> *They should not have to bother with the nasty complexity of parsing text and figuring out how to integrate with different plattforms and keeping apps follow a design pattern.* 
>
> *I want to bring them the power to focus on building digital assistant apps and let Pyttman take care of the boring parts.*
>
> */Simon Olofsson, creator of the Pyttman Project*



### A few bullet points are:

* Bundled with client classes already written and integrated with the framework, so you can focus on building your app and have it online on Discord with the ready-made DiscordClient.

* Develop your app once and chat with it on muliple platforms simultaneously by using multiple Client configurations in `settings.py`.

* No more tangled if-statements for deciphering a user command based on certain words. 

* API's for internal storage management, identifying entities (information in natural languare), scheduling of function / method calls,

* 100% object-oriented with base classes for subclassing as an alternative to using the presets.

* A clear and consice structure for how your app can be built and scale, with a directory structure set up for you.

* Offers a familiar syntax for developers with previous experience in [Django](https://www.djangoproject.com)

* Easy to use for simple projects - powerful and flexible for more complex projects

* Contains logging, scheduling and built-in client support for major platforms

  


### Get started

It's very easy to get started with Pyttman. 

1. Install it using pip: `pip install pyttman`
2. Navigate to the directory where you want to develop your Pyttman app
3. Start a project using the command `pyttman-cli newapp <app_name>`
4. You now have a template Pyttman app. Run it with the shell client using `pyttman-cli dev <app_name>`, or add clients to `settings.py` and have your digital assistant app up in seconds.
5. Consult the documentation for guidance on how to use Pyttman to its full potential by integrating your app with a chat service or your own website.
   


### Contributions

Contributions are more than welcome - write your PR in a branch named 'contribution-<my_contrib>' ideally.



### Open source notices
On behalf of the Pyttman dev team, thank you to all developers who worked on the following dependencies:

* Pyttman uses [Py7zr](https://github.com/miurahr/py7zr) for extractions 
* Pyttman uses [MultiDict](https://github.com/aio-libs/multidict) in its scheduler API 
* Pyttman uses [pytz](https://pythonhosted.org/pytz/) for timezones
* Pyttman uses [requests](https://docs.python-requests.org/en/master/) in tools offering easier API integration
* Pyttman uses [discord.py](https://github.com/Rapptz/discord.py) when adding support for native development of apps integrated with the [Discord](https://discord.com/) platform. discord.Client and discord.Message are subclassed. 

