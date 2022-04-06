# Pyttman Changelog




# v 1.1.11
**2022-**

This release improves the **EntityParser** API, packs the new `create 
ability` command for the `pyttman` cli tool, and introduces a 
few new other features and bugfixes.

### :star2: News
* New EntityField classes

  * The `TextEntityField` can now also be used as `StringEntityField` and 
    `StrEntityField`
  
  * The `IntegerEntityField` can now also be used as `IntEntityField`


* New command for `pyttman` cli: `create ability` 
  
  You can now create new ability modules with the Pyttman cli tool 
  `pyttman` from your terminal shell. A new module is created with 
  `ability.py`, `intents.py` and `__init__.py` file inside. Our ambition is 
  that this further improves the simplicity of developing apps with Pyttman,
  by streamlining the way applications grow.  


* `pyttman.app` 

  In Pyttman, you now have access to your application represented as the 
  `app` object, which you can import from pyttman as:  `from pyttman import 
  app` in any file inside your project. On this object you have access to 
  `settings`, `abilities` and `hooks` (mentioned further down) - which 
  empowers you to inspect and modify the state of your app down the road. 


* **Project templates** 

  The project template, used when creating new projects, is no longer shipped 
  with the project through PyPi, but 
  rather downloaded from an official GitHub repository, lowering the 
  payload when installing the package and ensures distributions always use 
  the latest templates.


* **Lifecycle Hooks**

  Lifecycle hooks allows you as a developer to have code executed in 
  certain timepoints in the lifecycle of your application. 
  * **Ability** lifecycle hook: 'before_create' allows you to execute code 
    before a certain Ability is loaded. This is useful to pre-populate the 
    `storage` object as `self.storage['foo'] = 'bar'` before the ability is 
    loaded.
  
  * `app` lifecycle hooks allows you to import the app you've developed as: 
    `from pyttman import app`, and then decorating any function in the 
    application as `@app.hooks.run('before_start')` allows you to run a 
    function before the entire app starts. This is useful for connecting to 
    databases or performing other tasks necessary to the application. 
    > **You can only decorate functions as app-lifecycle hooks from a 
    special module in your app: `app.py`. This module is automatically 
    imported at the start of the runtime, by Pyttman, if present in the app 
    root directory.** 


* **Introducing support for params in `EntityField` classes to be callable**
  
  A select set of arguments provided to EntityField classes such as 
  `StringEntityField` and others, can now be callables. This allows you as 
  a developer to have rules for EntityField classes evaluated at runtime, 
  and not when the app starts. This is useful for scenarios where you'd 
  want data from a dynamic source to control the behavior of an EntityField,
  say the available users in your app. 
 
  **Example**: `username = 
  StringEntityField(valid_strings=get_enrolled_usernames)`


### 👀 Changes

  > Note! This is a breaking change.
* **Further expansion of the Pyttman Middleware epic**

  In applications, the `settings.py` setting called `MESSAGE_ROUTER` 
  changes name to `MIDDLEWARE`. This is a part of the movement toward 
  supporting more flexible and powerful plugins in Pyttman, where the 
  MessageRouter belongs as a part of this Midde-ware ecosystem.
  In new apps, this setting has the updated name automatically. In apps 
  from previous versions of Pyttman, you must change this name in `settings.py.`


* **Refactored the `Message`, `Reply` and `ReplyStream` classes import path**
  
  This update moves the above mentioned classes. Change imports 

   **from:**
    
    `from pyttman.core.communication.models.containers import Reply, ReplyStream, Message`
  
    **to:**
  
     `from pyttman.core.containers import Reply,  ReplyStream, Message`
* 

### **🐛 Splatted bugs and corrected issues** 
* **Fixes [#58]((https://github.com/dotchetter/Pyttman/issues/58)**
* **Fixes [#62]((https://github.com/dotchetter/Pyttman/issues/58)**
  
  


# v 1.1.10
**2022-02-28**

This release further improves the new Plug-And-Play EntityField classes used in the EntityParser API in Pyttman; further empowering developers to quickly find words of interest in Messages from users, using the declarative EntityParser API. 

### :star2: News
* **Major refactoring of internal API algorithms to improve speed and** 
  **functionality of the EntityParser API.**

* **New EntityField: `BoolEntityField`**
  
   The `BoolEntityField` provides a boolean entity on whether a pattern 
    was matched in an incoming message, or not. This is useful for 
    scenarios when the word itself in the message is not of interest, but 
    only the fact if it occurred in the message at all.
   
     ```python
      # message.entities["answer_in_spanish"] will be True or False
      # depending on whether the message contains the word 'spanish'
      
      class EntityParser:
         answer_in_spanish = BoolEntityField(message_contains=("spanish",))
     ```
  
  
  
* **Added 2 new Identifier classes** 
  
  * `FloatIdentifier` and `NumberIdentifier` are both Identifier classes to 
    find numbers, and are direct references to `IntegerIdentifier` but 
    offers more naming options.
    
    
  
* **New settings.py option**
  The option to log to STDOUT in addition to the default log file has been added. To use it, define `LOG_TO_STDOUT = True` in the Pyttman app `settings.py` file.
  
  
  
* **Introducing Pyttman Middleware**

  The Pyttman framework is growing. To make it easier to extend functionality for developers using Pyttman, we have abstracted the layer for message routing to a new layer; the Middleware layer. 

  This allows for future extension of the Middleware layer, adding options for message filtering and reply relaying through event schedulers and much more. As of this release, nothing has really changed in the usagae experience, except for the deprecation warning on importing the `FirstMatchingRouter` through the legacy import path, since it was moved. No direct action is required for apps upgrading from older versions.

### **🐛 Splatted bugs and corrected issues** 
* **Fixes [#57](https://github.com/dotchetter/Pyttman/issues/57) - Logs don't show in Heroku**
  
  > This issue traces back to the way certain platform log the STDOUT and 
  > STDERR streams by default. We added a new optional setting which allows 
  > apps to also log to STDOUT: `LOG_TO_STDOUT = True` in `settings.py` in a 
  > Pyttman app will resolve this issue.

### 👀 Changes

* **Pyttman 1.1.10 requires Python 3.10 at minimum.** 

  Changes to the type hinting in several places in the source code means that Python versions below 3.10 are not supported. 

  > Note! This is a breaking change.

* **The usage of `Parser` classes in `EntityParser` classes in `Intent`** 
  **classes have been deprecated and are no longer supported.** Refer to the 
  `EntityField` types for direct replacements. `EntityField` classes 
  implement the same interface as the `Parser` classes.
  
   > Note! This is a breaking change.
  
* **`Identifier` classes are moved from `pyttman.core.parsing.identifiers` to `pyttman.core.entity_parsing.identifiers` module.**

  > Note! This is a breaking change.

* **The `ChoiceParser` class is deleted, in favor of using `TextEntityField` with `valid_strings` as the subset of available options.**

  > Note! This is a breaking change.

* **Reverts the change made in** `1.1.9` with Entities: `message.entities` is 
  now back to being a dict of direct entity values, not `Entity` classes. 
  The reason for this revert was the repetitive pattern of using the 
  `.value` property in apps on properties, and not doing so would cause 
  exceptions.
  
    > Note! This is a breaking change.

* **The Middleware API in Pyttman results in a move of the** `FirstMatchingRouter` class, commonly referenced in Pyttman apps in `settings.py` under `ROUTER_CLASS`. The class is now available under `pyttman.core.middleware.routing.FirstMatchingRouter` but is still available for import at the older import path, `pyttman.core.parsing.routing.FirstMatchingRouter` for the time being, which results in a deprecation warning to STDOUT.




# v 1.1.9.1
2021-12-24

This release is a hotfix release of a critical bug in the Pyttman cli, 
rendering apps unable to start in client mode, rendering them unusable.

### **🐛 Splatted bugs and corrected issues** 
* Fixes [#55](https://github.com/dotchetter/Pyttman/issues/55) - pyttmancli runclient not working

# v 1.1.9
2021-12-11

This release includes bug fixes but also some new cool features.

### :star2: News
* Entities are now accessed on the `Message` object in Intents instead of 
  being accessed on the Intent itself. 
  Accessing Entities on the Intent is supported until 1.2.0 and will raise 
  a deprecation warning.
* **EntityField**  classes provide an easier and more efficient way to find 
  values of interest in messages from users. 

### **🐛 Splatted bugs and corrected issues** 
* Fixes [#47](https://github.com/dotchetter/Pyttman/issues/47) - Strings with different case from otherwise identical values in lead/trail/exclude are not truncated
* Fixes [#48](https://github.com/dotchetter/Pyttman/issues/48) - ChoiceParser can't parse choices when capitalized
* Fixes an issue with type hinting referring to the `MessageMixin` in `Intent.respond()` implementation -> Corrected to now hinting `Message`.
  
### 👀 Changes
* Entities are no longer `str`, but `Entity` instances. To fetch the value 
  of the entity itself as previously done by `name = self.entities.get
  ("name")` is now instead done as `name = self.entities.get("name").value`

# v 1.1.8

This release includes bug fixes and internal improvements mainly. 

Although the points listed below may seem minor, we've rewired and tested this release probably better than any other up to this point :happy:



### :star2: News

* **New setting in  `settings.py`**

  `settings.py` in Pyttman apps now have the `DEV_MODE` flag for users to toggle. 

  > Note! When you run an app in dev mode using `pyttman dev <app_name>`, it is automatically set to `True` regardless of `settings.py`. 

  *Example*:

  ```python
  # In settings.py
  DEV_MODE = True
  
  # Somewhere in the app logic
  if pyttman.settings.DEV_MODE is True:
  	print("Some debug statement")
  ```

  

### 👀 Changes

* The `BaseClient` class is moved in Pyttman, which changes the import path for the class:

  `pyttman.clients.builtin.base.BaseClient`  becomes  `pyttman.clients.base.BaseClient` .

* Vast improvements to the Pyttman CLI tool

  The administrative CLI tool `pyttman` for creating, bootstrapping and 
  debugging Pyttman apps has been rewritten using the Pyttman framework 
  itself to build Intents, read from the terminal shell. 



### **🐛 Splatted bugs and corrected issues** 

* Fixes [#35](https://github.com/dotchetter/Pyttman/issues/35)  with internal improvements to the EntityParser algorithm in how it considers the resolution order of how entity strings are parsed, identified and later stored in `self.entities` in `Intent` classes.
* Fixes [#40](https://github.com/dotchetter/Pyttman/issues/40) - `pyttman dev <app name>` now works without providing a Client class.





# v 1.1.7

This release is a hotfix release, adressing issues using the `runclients` command with `pyttman` cli tool on linux and unix based systems. 

### 👀 Changes
* Clients are no longer started in parallel using Threading due to issues with security and runtime on unix and linux based systems. Observe that in your `settings.py` file, the `CLIENTS` field is replaced by a  `CLIENT` field, which is a single dictionary containing the client configuration for your app. This was necessary for multiple reasons, one being the complexity of pickling application logic to run them in parallel using  a process pool instead of threading, to solve [bug #33](https://github.com/dotchetter/Pyttman/issues/33). We're sorry about the inconvenience this may cause for your development and the experience with Pyttman so far. We're still learning.
  It seems that this approach works well with deploying apps using Docker, as you can create containers using different settings for various platforms and support multiple platforms in this manner.
  
  > Note! This is a breaking change.
  
* The Pyttman CLI "`pyttman`" argument for running client has changed from `runclients` to just `runclient`, indicating a `single` client configuration in settings.py
  
  > Note! This is a breaking change.

### 🐛 Splatted bugs and corrected issues 
- Fixes an [issue](https://github.com/dotchetter/Pyttman/issues/33), causing the `runclients` argument not to start apps as intended on linux and unix based operating systems.


- Improves how settings are loaded, using the new [Setting](https://github.com/dotchetter/Pyttman/blob/c9f4433d3221b8fd30d71cecdece84b0bb05a4db/pyttman/core/internals.py#L46) class.
  You still access your settings defined in `settings.py` using `pyttman.settings` in your app.

# v 1.1.6



### 🤗 New features and changes
* The `Feature` class is renamed to `Ability` for better semantic similarity to the general standard of terminology.
  
  > Note! This is a **breaking** change.


* The `Command` class is renamed to `Intent` for better semantic similarity to the general standard of terminology.
  
  > Note! This is a **breaking** change.


* `pyttman-cli` is renamed to just `pyttman` for increased simplicity.
  
  > Note! This is a **breaking** change.


* The reference to `Feature` in `Intent` classes (previously `Command` classes) - is removed. 
  this means that the `Storage` object previously accessed through `self.feature.storage` can no longer be accessed this
  way. Instead, the `Ability` is no longer referenced inside `Intent` classes for cleaner OOP relations. 
  **However**, the `Storage` object is still available in `Intent` classes, of course. It is accessed using `self.storage` both in the `Ability`
  and in `Intent` classes.
  
  > Note! This is a **breaking** change.


* The NLU component `EntityParser` class of `Intent` classes has been improved, and no longer identifies one entity more than once. It is also a lot smarter in how it traveres the message in order to find the data of interest.


* The `EntityParser` class must no longer inherit from `EntityParserBase` or `Intent.EntityParser`, metaclassing is internally handeled.


* The `CommandProcessor` class which was deprecated in version 1.1.4, is removed.


* The `Callback` class which was deprecated in 1.1.4, is removed.


* The `Interpretation` class which was deprecated in 1.1.4, is removed.


* Methods associated with legacy classes from the `Intent` and `Ability` classes internally, have been removed


* The new `ReplyStream` Queue-like object offers you the ability to return **multiple** response messages in a single object from Intents.
The `ReplyStream` will wrap your strings or other objects as `Reply` objects if compatible, and the client will post each of these elements as separate messages in the client. 


* The `pyttman.schedule.method` api method no longer requires the use of the `async_loop` argument if the function to be scheduled is asynchronous, but rather acquires the running loop through `asyncio.get_running_loop()`. If no running loop is identified, it will automatically run the asynchronous function using `asyncio.run`. 


* Identifier class `DateTimeStringIdentifier` has added regex patterns to also identify strings with a date stamp, without a specific time. 
  For example, in a message like: `On that fateful night of 1986/04/26 (...)` - the `DateTimeStringIdentifier` would now find `1986/04/26` as a valid entity. 


### 🐛 Splatted bugs and corrected issues 

* Fixes an [issue](https://github.com/dotchetter/Pyttman/issues/30) where line separations in `Reply` objects were not present when the data was displayed in applications such as DIscord or the Cli client terminal shell. These are now present.


* Fixes an [issue](https://github.com/dotchetter/Pyttman/issues/24) where clients could not communicate any errors upon startup. These are now showed through user warnings.


* Fixes an [issue](https://github.com/dotchetter/Pyttman/issues/31) where one element in a message would end up multiple times in `self.entities` incorrectly


* Fixes an [issue](https://github.com/dotchetter/Pyttman/issues/32) where strings defined in `lead` and `trail` in `Intent` classes were case-sensitive - they are not anymore.


* Fixes an issue where an entity parsed using a `ChoiceParser` would
  be stored as the casefolded variant. With this correction, identification
  is done case-insensitively, and the defined value in the `ChoiceParser.choices`
  is the one present in `self.entites`, when a match occurs.


* Fixes an issue with the `CapitalizedIdentifier` identifier class, as it would not grant
  all-caps words as valid.
------



# v 1.1.4



## Native client support for community plattforms		

> **This feature is one of the flagship-features of this release.**  


A new interface class, `BaseClient` dictates how Pyttman expects a minimally developed client to behave. 

This allows us to subclass platform clients from SDK's and libraries from plattforms, and using the `BaseClient` as a mixin, creating the powerful combination of a native client to be used with Pyttman.

The native and community Client support in Pyttman enables you to launch your app to the [Discord](https://discordpy.readthedocs.io/en/stable/api.html) plattform **without a single line of code.** 

By simply providing which clients you want to use in the `settings.py` file ( using Pyttman-included Clients, or a client you wrote yourself )  - your app will be running on all clients in parallel by starting your app with `pyttman-cli runclients`.  

The Pyttman `MessageRouter` will keep your clients separate, so there's no risk of a `Reply` ending up in the wrong plattform. 

Many more clients are on the way, so stay tuned for more plattform clients to be supported natively.



> **Note**
>
> Some platforms offer different methods than others; if you mix plattform clients in your app, it's a good idea to check which client is associated with your message, if you're accessing members of that client. 



*Example*

```py
# The following CLIENTS list will start your app using the Discord client 
# making your bot go online, with your Pyttman app powering it's backend.
# To use more clients, simply append more config dict's like this one, and 
# have your app hosted on these platforms in parallel.

CLIENTS = [
	{
		"module": "pyttman.clients.community.discord.DiscordClient",
		"token": "foo-token-from-discord-developer-portal",
		"guild": "bar-guild-id-from-your-discord-server"		
	}
]
```



* **Parallel runtime for all clients**

  Develop your app **once** - and have it online on multiple platforms in an instant. Add the clients you want to use to the `CLIENTS` list in `settings.py`. That's it! 

  The next time you run `pyttman-cli runclients` , the clients start up in parallell and inside your app, you will see which client is sending the message by the Message property `client`. 

  

  *Example*

  ```py
  # inside a Command.respond method:
  
  if isinstance(message.client, DiscordClient):
  	print(message.client.users)
  elif isinstance(message.client.CliClient):
  	message.client.publish("I can publish this directly to my CliClient for testing!")
  ```

  

> **Hint!**
>
> If you're a power user and want to use the hooks defined in `discord.Client`, simply subclass `DiscordClient ` to have the Pyttman-defined  '`on_message`'  hook method already taken care of (this is where the integration takes place between your Pyttman app and Discord) and define any behavior in the other hooks as you please. Use your custom class instead of the included one, in the example above. 





## EntityParser API

> **This feature is one of the flagship-features of this release.**  

The EntityParser is a powerful tool for developers looking to extract information from natural language. 

Odds are you're developing a chatbot using Pyttman. Chatbots usually have a job to do, and more than often, we as devs, are looking for data in the message from a user. 

A message from a user may look something like this:



>  `Can you play Rocket Man by Elton John on Spotify please?`



In this example, you may have a Command which job it is to play songs for users on their Spotify accounts. 

Now, your app may host support for more platforms than just one. Say you also support SoundCloud, or YouTube Music. You'd want to identify which platform the user wanted to use. 

You're also looking for `artist` and/or `song` in this message. 

The **EntityParser** class defined *inside* your Command will take care of this for you. It enables you to quickly and without a single iteration or if-statement, find the values you're looking for by defining a set of rules to wich degree is entirely up to you - loosely or constricted.



*Example*

```py
class PlayMusic(Command):
    lead = ("play",)

    """
    Define the EntityParser inside the Command class and 
    create fields, named as you want them to be named when
    accessing them through self.entities.get(). 
    """

    class EntityParser(Command.EntityParser):
        song = ValueParser(identifier=CapitalizedIdentifier, prefixes=("play",), span=10)
        artist = ValueParser(identifier=CapitalizedIdentifier, prefixes=("by",), span=2)
        platform = ChoiceParser(choices=("Spotify", "SoundCloud", "YouTubeMusic"))

    def respond(self, message: MessageMixin) -> Reply:
        print("My entities:", self.entities)
        return Reply(self.entities)


class MusicFeature(Ability):
    commands = (PlayMusic,)


```

Writing the message to the following example command returns:

```py
{'artist': 'Elton John', 'platform': 'spotify', 'song': 'Rocket Man'}
```



This is a short example of how powerful the EntityApi is, and what you can do with it. 

In short - it enables you to develop Commands and Features which extract information from messages, without looping manually, looking for data. 





## Storage API

* Ability-level implicit encapsulation, dict-like storage in all `Command` classes. 

  The Storage API offers a `Storage` object accessible in all `Command` subclasses by accessing  the `self.feature.storage` property.  Your other Commands which are defined in the same `Ability` will access the same storage object which allows for an easy and safe way to store and share data between commands. 

  

  *Example*

  ```py
  # Put data
  class FooCommand(Command):		
  	def respond(self, Message):
  		# self.feature.storage["foo"] = "bar" works as well
  		self.feature.storage.put("foo", "bar") 
  
  # Get data 
  class BarCommand(Command):
  	def respond(self, Message):
  	foo = self.feature.storage.get("foo")
  	print(foo)
  	
  class FooBarFeature(Ability):
  	commands = (FooCommand, BarCommand)
  
  ```

  **Outputs:**

  `>>> "bar"`

  

  The Storage object is encapsulated by the scope of a `Ability` in which the command is listed in. This means that `Command` classes operate on the same `Storage` object as the other `Command` classes in the same `Ability`, but commands outside of the Ability cannot interfere with the data in that storage object. 

  

  > **Note**
  >
  > If you don't use the Storage API but try to use instance variables in your commands, you will eventually learn that they don't stick. This is because of how Pyttman preserves memory in deleting Command instances once the Reply is generated. 

  

  

## Improved settings module

* Improved versatility with configuration for default replies vastly improved and other similar settings

* AutoHelp, creating automatically generated help snippets for your Commands by their configuration
* Improved error handling
* If exceptions occur in the application, the user will in 99% of the times receive a mesage letting them know something went wrong instead of the app going silent. The app is much less likely to crash, and a UUID is stored in the log file along with a stderr print out of the error. The user also gets to see thsi UUID for relaying to a developer if needed.



## Routing

MessageRouters improved, now instantiating Command classes each time to prevent memory leaks in local preferences in Command objects outside of the Storage API.



## Licenses

This release includes discord.py, and it's license is mentioned in the README.MD and LICENSE of the Pyttman project, [here](https://github.com/dotchetter/pyttman)
