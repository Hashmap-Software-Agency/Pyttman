import json
import requests
from datetime import datetime

"""
Details:
    2020-07-05
    
    pytman framework apihandles source file

Module details:
    
    This file is designed to hold classes and / or
    functions that make interacting with various
    API's easier.
"""


class RestApiHandle:
	"""
	Call api and parse output to JSON. Returns cache 
	unless the data over 2 hours old by default as to not 
	overload the api service. The object calls the api upon
	instantiation, and will automatically cache the response.

	:uri:
		URI for the REST api

	:_last_api_call:
		datetime stamp for when data was most recently fetched
		from the api, used to return cache within the defined
		span upon construction, minmum 0 hours.

	:_wait_time:
		seconds calculated by the defined standby_hours parameter

	:_cached_response:
		last response received by the API

	:_headers_:
		dictionary which can be added to with the add_header method.
		Contains headers which will be used upon a request with the 
		fetch() call.
	"""

	def __init__(self, uri: str, standby_hours = 2):
		self.uri: str = uri
		self.last_api_call: datetime = None
		self._wait_time = (60 * 60) * standby_hours
		self._cached_response = None
		self._cached_response: dict = None
		self._headers = {}

	@property
	def uri(self) -> str:
		return self._uri
	
	@uri.setter
	def uri(self, uri: str) -> None:
		self._uri = uri
		if not uri.startswith('https'):
			raise Warning('pytman RestApiHandle - Security Warning: Got "http", expected "https"')
	
	@property
	def last_api_call(self) -> str:
		"""
		Return property in string format for easy readability
		for users.
		"""
		return self._last_api_call.strftime("%Y-%m-%d %H:%M")

	@last_api_call.setter
	def last_api_call(self, val: datetime) -> None:
		self._last_api_call = val

	def add_header(self, key: str, value: str) -> None:
		"""
		Allows this object to add HTML headers for the 
		request. The method is meant to be used prior to
		a call for an API which requires headers to work.

		:param key:
			str
			the key in the header, example: 'User-Agent'
		:param vaue:
			str
			The value behind said key.
		:returns:
			None
		"""
		self._headers[key] = value

	def get(self) -> dict:
		"""
		Call the api and mutate the instance variable _cached_response
		at the same time, if either none prior were made or the time 
		expired and it needs to be refreshed. 

		:returns:
			dict
		"""
		if self._cached_response:
			seconds_since_last_call = (datetime.now() - self._last_api_call).seconds
			if seconds_since_last_call < self._wait_time: 
				return self._cached_response
		try:
			response = requests.get(self.uri, headers = self._headers).json()
		except Exception:
			raise
		
		self._cached_response = response
		self.last_api_call = datetime.now()
		return response

	def post(self, headers: dict) -> dict:
		"""
		Send a POST request to the API uri configured.
		since the headers are ambigous for this class
		they have to be specified by the caller. Only
		dictionaries are accepted for this parameter.

		:param headers:
			dictionary with POST request headers for
			the call you wish to make to the API.
			Example: {'language': 'english'}
		:returns: 
			dict, response from the API response.
		"""
		return json.loads((requests.post(url = self.uri, data = headers)).text)