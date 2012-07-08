"""
*************************************************************************************
* @author: Ferdinand E. Silva
* @email: ferdinandsilva@ferdinandsilva.com
* @title: Rhythmbox To Twitter
* @description: Post the title of currently playing song of Rhythm Box to Twitter
*************************************************************************************
"""
class InvalidTwitterAccountException(Exception):
	pass
	
class InvalidCustomMessageException(Exception):
	pass