from Summarizer import *
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

class Info:
	"""Class that handles the information for the article and is also responsible
	for obtaining the summary for the article.
	"""
	
	def __init__(self, url, keyword_limit, sentence_limit):
		"""
		Initialization function for this class.
		
		Parameters:
			1) url - url to visit to gather information
			2) keyword_limit - use this many keywords when using algorithm
			3) sentence_limit - floating percentange that limits the amount of sentences gathered
		"""
		
		self.url = url
		self.summary = Summarizer(url, keyword_limit, sentence_limit)
		self.soup = self.open_url()
		self.title = None
		self.author = None
		self.description = None
		self.url = None
		
	def run(self):
		"""Driver function for this class."""
		
		#Gather relevant info
		self.gather_info()
		
		#Print relevant info to text file
		self.print_info()
		
		#Grab text from contents and pass to Summarizer module
		text = self.summary.clean_text()
		
		#Obtain summary
		summary = self.summary.grab_summary(text)
		
		#Print summary to text file
		self.summary.print_summary(summary)
		
		
	def open_url(self):
		"""Open the url and return the contents."""
		
		try:
			response = urlopen(self.url)
			html = response.read()
			soup = BeautifulSoup(html, "html.parser")
		
		except OSError as e:
			if e.code == 503:
				print("Querying site again!")
				return self.open_url()
			
		return soup

	def gather_info(self):
		"""
		Parse the contents of the soup in order to obtain the title, author, description and url
		for the article.
		"""
		
		self.title = self.soup.find("meta", attrs={"property" :"og:title"})
		self.author = self.soup.find("span", attrs={"class": "author"})
		self.description = self.soup.find("meta", attrs={"property" : "og:description"})
		self.url = self.soup.find("meta", attrs={"property" : "og:url"})
		
	def print_info(self):
		"""Print out the relevant info where applicable."""
		
		if self.title:
			self.title = self.title["content"]
		
		if self.author:
			self.author = self.author.text
			split_author = self.author.split()
			if len(split_author) > 2:
				self.author = ""
				for obj in split_author:
					self.author = self.author + " " + obj
		
		if self.description:
			self.description = self.description["content"]
		
		if self.url:
			self.url = self.url["content"]
		
		#Write all the information to a text file that can handle utf-8 to avoid encoding errors.
		with open("encoded.txt", "wb") as encoder:
			encoder.write(("Title: {}\n".format(self.title)).encode('utf-8'))
			encoder.write(("Author: {}\n".format(self.author)).encode('utf-8'))
			encoder.write(("Description: {}\n".format(self.description)).encode('utf-8'))
			encoder.write(("Url: {}\n".format(self.url)).encode('utf-8'))
		
def main():
	"""Driver function to run the program."""
	url = "https://en.wikipedia.org/wiki/Ant"
	
	info = Info(url, 25, 0.65)
	info.run()

		
if __name__ == "__main__":
	main()	