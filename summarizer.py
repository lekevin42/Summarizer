from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import OrderedDict

class Summarizer:
	def __init__(self, url, keyword_limit, sentence_limit):
		self.url = url
		self.keyword_limit = keyword_limit
		self.sentence_limit = sentence_limit
		self.sent_count = None

	def clean_text(self):
		lines = []
		unclean_text = []
		buffer = []
		
		response = urlopen(self.url)
		html = response.read()
		soup = BeautifulSoup(html, "html.parser")

		# kill all script and style elements
		for script in soup(["script", "style"]):
			script.extract()  

		text = soup.get_text()
		
		#remove leading and trailing space on every line
		for line in text.splitlines():
			lines.append(line.strip())
		
		#split lines into singular lines
		for line in lines:
			for word in line.split("  "):
				unclean_text.append(word.strip())
		
		#remove empty lines
		for sent in unclean_text:
			if sent:	
				buffer.append(sent)
		
		text = '\n'.join(buffer)

		return text

	def ignored_word(self, word):
		with open("ignored_words/ignored_words.txt", "r") as ignored_words:
			for ignored_word in ignored_words:
				if word == ignored_word.strip():
					return False
				
				elif word == (ignored_word[0:1].upper() + ignored_word[1:]).strip():
					return False
					
				elif word == (ignored_word.replace("\n", ",\n").strip()):
					return False
					
				elif word == (ignored_word.replace("\n", ".\n").strip()):
					return False
					
		return True
		
	def grab_keywords(self, text):
		dict = {}
		keywords = []
		counter = 0
		
		for sent in text:
			split_text = sent.split()
			for word in split_text:
				if self.ignored_word(word) and word[0].isupper():
					if word in dict:
						dict[word] += 1
					
					else:
						dict[word] = 0
						
		dict = self.check_duplicates(dict)
				
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
			
		for k, v in dict.items():
			if counter != self.keyword_limit:
				keywords.append(k)
				counter += 1
		
		return keywords

	def check_duplicates(self, dict):
		count = 0
		dup_list = []
		
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		
		dup_list.append(list(dict.items())[0][0])

		for k, v in dict.items():
			for word in dup_list:
				if word != k:
					if k.find(word) != -1:
						dict[k] = 0
		
		dict = OrderedDict(sorted(dict.items(), key=lambda t: t[1], reverse=True))
		return dict
		
		
	def grab_summary(self, text):
		summary = []

		text = self.mark_end_of_paragraphs(text)
		
		text = self.split_text(text)
		
		self.sent_count = len(text)
		
		keywords = self.grab_keywords(text)
	
		#for k in keywords:
		#	print(k.encode('utf-8'))
	
		best_sentences = self.rank_sentences(text, keywords)
		
		for index in best_sentences:
			summary.append(str(text[index]))
			
		summary = self.group_summary(summary)
		
		return summary
	
	def group_summary(self, summary):
		grouped_summary = []
		s = ""
		
		for sent in summary:
			if s.find("@") != -1:
				s = s.replace("@", " ")
				grouped_summary.append(str(s) + "\n")
				s = ""
			s += sent
			
		return grouped_summary
		
	
	def split_text(self, text):
		sentences = []
		buffer = []
		finalized_sentences = []
		puncts = [".", "?", "!"]
		
		text = self.replace_text(text)
		
		for sent in text.splitlines():
			if self.has_punct(puncts, sent):
				sentences.append(sent)
		
		for sent in sentences:
			fs = sent.split(". ")
			buffer.append(fs)
		
		for s in buffer:	
			for t in s:
				if t != "":
					finalized_sentences.append(t + ".")
		
		count = 0
		for sent in finalized_sentences:
			finalized_sentences[count] = finalized_sentences[count].replace("..", ".")
			count += 1
		
		return finalized_sentences
		
	def replace_text(self, text):
		with open("replaced_words/replaced_words.txt", "r") as replaced_words:
			for word in replaced_words:
				delimiter = word.find("=")
				replaced_word = word[0:delimiter]
				replacer = word[delimiter+1:]
				
				text = text.replace(replaced_word, replacer)
				
		return text
		
	def has_punct(self, puncts, sent):
		for punct in puncts:
			if sent.find(punct) != -1:
				return True
				
		return False
				
	def rank_sentences(self, text, keywords):
		sentence_dict = {}
		sentence_count = 0
		best_sentences = []
		count = 0
		
		for sent in text:
			rank = self.check_keywords(sent, keywords)
			sentence_dict[sentence_count] = rank
			sentence_count += 1
		
		sentence_dict = OrderedDict(sorted(sentence_dict.items(), key=lambda t: t[1], reverse=True))
		
		for key, value in sentence_dict.items():
			if count < self.sentence_limit * self.sent_count:
				best_sentences.append(key)
			count += 1
			
		best_sentences.sort()
		
		return best_sentences
		
			
	def check_keywords(self, sent, keywords):
		rank = 0
		split_sent = sent.split()
		
		for word in split_sent:
			if keywords.count(word) > 0:
				rank += 1
		
		return rank

	def mark_end_of_paragraphs(self, text):
		text = text.replace("\n", "@\n")
		return text

		
def print_summary(summary):
	for sent in summary:
		try:
			print(str(sent))
		except UnicodeEncodeError:
			print(str(sent.encode('utf-8')))
			
def main():
	#url = "http://www.popsci.com/can-classic-thought-experiment-explain-trumps-win"
	
	url = "http://bleach.wikia.com/wiki/Ichigo_Kurosaki"
	
	#url = "http://www.popsci.com/neanderthals-may-have-given-us-genital-warts"
	
	#url = "http://bleach.wikia.com/wiki/Aizen"
	
	summarizer = Summarizer(url, 25, 0.5)
	
	text = summarizer.clean_text()
	
	summary = summarizer.grab_summary(text)
	
	print_summary(summary)
	
if __name__ == "__main__":
	main()