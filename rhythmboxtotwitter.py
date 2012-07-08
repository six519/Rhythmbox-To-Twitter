from twython import Twython
from urllib2 import urlopen,Request,build_opener,HTTPCookieProcessor,install_opener
from urllib import urlencode
from cookielib import LWPCookieJar
from HTMLParser import HTMLParser
import dbus, gobject, dbus.glib, os
from twitter_exceptions import InvalidTwitterAccountException, InvalidCustomMessageException

class RhythmBoxToTwitter(HTMLParser):
	
	def __init__(self,consumerKey,consumerSecret,twitterUsername,twitterPassword):
		HTMLParser.__init__(self)
		self.consumerKey = consumerKey
		self.consumerSecret = consumerSecret
		self.twitterPassword = twitterPassword
		self.twitterUsername = twitterUsername
		self.jarName = 'cookie.jar'
		self.tokens = {}
		self.cnt = 0
		self.twitter = None
		self.__customMessage = None

	def handle_starttag(self, tag, attrs):
		if tag == 'input':
			if self.cnt == 0:
				self.tokens['authenticity_token'] = attrs[2][1]
				self.cnt += 1
			elif self.cnt == 1:
				self.tokens['oauth_token'] = attrs[3][1]
				self.cnt += 1
				
	def setCustomMessage(self, msg):
		try:
			testString = msg % ("test","test")
			self.__customMessage = msg
		except (TypeError, ValueError):
			raise InvalidCustomMessageException("Invalid Custom Message")
				
	def postMessage(self,msg):
		self.setTwitter()
		self.twitter.updateStatus(status = msg)
		
	def listening_to(self,*args, **kwargs):
		mydict = self.rhythmshell.getSongProperties(self.rhythm.getPlayingUri())		
		ret = self.__customMessage % (mydict['artist'], mydict['title']) if self.__customMessage else "Listening To: %s - %s - http://bit.ly/If4RXN" % (mydict['artist'], mydict['title'])
		self.postMessage(ret)
		print ret
		
	def run(self):
		self.checkTwitterAccount()
		self.bus = dbus.SessionBus()
		self.rhythm_obj = self.bus.get_object("org.gnome.Rhythmbox", "/org/gnome/Rhythmbox/Player")
		self.rhythmshell_obj = self.bus.get_object("org.gnome.Rhythmbox", "/org/gnome/Rhythmbox/Shell")
		self.rhythm = dbus.Interface(self.rhythm_obj, "org.gnome.Rhythmbox.Player")
		self.rhythmshell= dbus.Interface(self.rhythmshell_obj, "org.gnome.Rhythmbox.Shell")
		self.bus.add_signal_receiver(self.listening_to,dbus_interface="org.gnome.Rhythmbox.Player",signal_name="playingChanged")
		loop = gobject.MainLoop()
		loop.run()

	def deleteJar(self):
		try:
			os.remove(self.jarName)
		except OSError:
			pass

	def setTwitter(self):
		self.resetData()
		
		try:
			self.twitter = Twython(twitter_token = self.consumerKey,twitter_secret = self.consumerSecret)
			auth_props = self.twitter.get_authentication_tokens()
		
			cookie = self.jarName
			cookieJar = LWPCookieJar()
			opener = build_opener(HTTPCookieProcessor(cookieJar))
			install_opener(opener)
		
			f = urlopen(auth_props['auth_url'])
			cookieJar.save(cookie)
			self.feed(f.read().decode('utf-8','replace'))
			self.close()
			f.close()
		
			post = {"session[username_or_email]":self.twitterUsername,"session[password]":self.twitterPassword}
			post.update(self.tokens)
			data = urlencode(post)
		
			cookieJar.load(cookie)
			f = urlopen("https://twitter.com/oauth/authenticate",data)
			f.close()
		
			self.twitter = Twython(
			twitter_token = self.consumerKey,
			twitter_secret = self.consumerSecret,
			oauth_token = auth_props['oauth_token'],
			oauth_token_secret = auth_props['oauth_token_secret']
			)
		
			authorized_tokens = self.twitter.get_authorized_tokens()
		
			self.twitter = Twython(
			twitter_token = self.consumerKey,
			twitter_secret = self.consumerSecret,
			oauth_token = authorized_tokens['oauth_token'],
			oauth_token_secret = authorized_tokens['oauth_token_secret']
			)
		except:
			raise InvalidTwitterAccountException("Invalid Twitter Account")
		
		self.resetData()

	def checkTwitterAccount(self):
		self.setTwitter()
        
	def resetData(self):
		self.deleteJar()
		self.tokens = {}
		self.cnt = 0

if __name__ == "__main__":
	try:
		twitterUsername = raw_input('Enter Twitter Username: ').strip()
		twitterPassword = raw_input('Enter Twitter Password: ').strip()
		rbox = RhythmBoxToTwitter("HGEEIDCqgsIjkdp8RdaDAA", "ILbpuyjhMtUVb1wWz1gD4QDPdWvA1Lro3NDb1ElicCY", twitterUsername, twitterPassword)
		#	Below (Set custom message)	
		#rbox.setCustomMessage("Artist %s and Title %s")
		rbox.run()
	except KeyboardInterrupt:
		print "\nApplication exits..."
	except InvalidTwitterAccountException:
		print "\nInvalid Twitter Account"
		print "\nApplication exits..."
	except InvalidCustomMessageException:
		print "\nInvalid Custom Message"
		print "\nApplication exits..."