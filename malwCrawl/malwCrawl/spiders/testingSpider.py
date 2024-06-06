import scrapy
import owlready2
import re
from bs4 import BeautifulSoup


class TestingspiderSpider(scrapy.Spider):
    name = "testingSpider"
    allowed_domains = ["www.csoonline.com"]
    start_urls = ["https://www.csoonline.com/article/572911/11-infamous-malware-attacks-the-first-and-the-worst.html"]

    def parse(self, response):
        # Load your ontology
        onto_path = "/Users/marekstrba/Documents/skola/bakalarka/malont/MALOnt.owl"
        onto = owlready2.get_ontology(onto_path).load()

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Directly extract text from paragraphs, ensuring proper spacing
        paragraphs = soup.find_all('p')
        clean_text = ' '.join(paragraph.get_text(" ", strip=True) for paragraph in paragraphs)

        # Find sentences with ontology terms
        matching_sentences = self.find_sentences_with_ontology_terms(clean_text, onto)

        # Save or process matching sentences...
        filename = 'crawled_websites.txt'
        with open(filename, 'a') as f:
            # Writing the URL of the currently scraped website
            f.write(response.url + '\n\n')

            # Writing matching sentences as a continuous block of text
            continuous_text = ' '.join(matching_sentences)
            f.write(continuous_text + '\n\n')

        self.log(f'Saved file {filename}')

        links = soup.find_all('a', href=True)
        for link in links:
            # Use the urljoin method to construct an absolute URL
            absolute_url = response.urljoin(link['href'])
            # Yield a new request for each found URL
            yield scrapy.Request(absolute_url, callback=self.parse)


    def extract_ontology_terms(self, onto):
        terms = set()
        for cls in onto.classes():
            terms.add(cls.name.lower())
        for ind in onto.individuals():
            terms.add(ind.name.lower())
        for prop in onto.properties():
            terms.add(prop.name.lower())
        return terms

    def find_sentences_with_ontology_terms(self, text, onto):
        terms = self.extract_ontology_terms(onto)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        matching_sentences = []

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in terms):
                matching_sentences.append(sentence)

        return matching_sentences
