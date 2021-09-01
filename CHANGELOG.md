# Pyttman Changelog



# v 1.1.5



### 🤗 New features and changes
* The `Feature` class is renamed to `Ability` for better semantic similarity to the general standard of terminology.
  > Note! This is a **breaking** change.


* The `Command` class is renamed to `Intent` for better semantic similarity to the general standard of terminology.
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