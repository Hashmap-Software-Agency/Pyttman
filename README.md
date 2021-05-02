# Pyttman 
#### The virtual assistant framework made for developers with ideas

Pyttman is a framework for developing virtual assistants, chatbots or other language driven applications. 
It houses base classes and ready-to-use classes, both for making powerful custom features, or using the 
ones already provided for you, as pluggable objects. 

It is highly inspired by Django, and aspires to offer a similar ease of use as Django does for web, but
for chatbots and personal digital assistants.



### Why use Pyttman?

Pyttman is a high level framework which abstracts away much of the hard work when developing natural-language-command-driven apps. 

**A few bullet points are:**

* No more tangled if-statements for deciphering a user command based on certain words. 
* 100% object oriented with base classes for subclassing as an alternative to using the presets.
* A clear and consice structure for how your app can be built and scale, with a directory structure set up for you.
* Loaded with tools such as:
  * **Scheduling**: One of Pyttman's most powerful punches is its scheduler. It can schedule your objects' methods or regular functions, both regular and `async`, with a great overview of how they run in the background with the `pyttman.schedule` api. Scheduled jobs are threaded, which makes your app safe from any hiccups during the run of a scheduled method - it won't interrupt your main loop. You can always control and view scheduled functions during runtime with the `pythman.schedule` api
  * **Logging:** Log your methods or functions by decorating them with `pyttman.logger.loggedmethod` to have them automatically log their output and any exceptions in a common log file for your app
  * **Callback, Feature, CommandProcessor** -  These objects lay the baseline for your app, by providing an easy api for binding commands to your functions, classes and/or methods.
  * **Client support:** Client support concists currently of Discord exclusively, more will be added as development proceeds.



### How to get started

It's very easy to get started with Pyttman. 

* Install it using pip: `pip install pyttman`
* Navigate to the directory where you want to develop your Pyttman app
* Start a project using the command `pyttman-cli newapp <projectname>`
* Use the created directories to build your app. Run it with main.py, which sets up Pyttman for you
* Add settings to `settings.py` as you wish and access them in your app through `pyttman.settings.setting_name` 
* Consult the documentation for guidance on how to use Pyttman to its full potential.



### Contributions

Contributions are more than welcome - write your PR in a branch branched from 'contributions' ideally.



