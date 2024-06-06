import scrapy
from bs4 import BeautifulSoup
from . import ontology_terms
class CsoonlineSpider(scrapy.Spider):
    name = "csoonline"
    allowed_domains = ["www.csoonline.com"]
    start_urls = ["https://www.csoonline.com/cybercrime/filter/feature/"]
    ontology_terms = ontology_terms

    custom_settings = {
        'DEPTH_LIMIT': 27,
        'FEEDS': {
            'crawledWebsites.json': {
                'format': 'json',
                'indent': 4,
            }
        },
        'ROBOTSTXT_OBEY': False,
        'AUTOTHROTTLE_ENABLED': True,
    }

    def parse(self, response):
        links = response.css('a.grid.content-row-article::attr(href)').getall()
        titles = response.css('h4.card__title::text').getall()
        descriptions = response.css('p.card__description::text').getall()

        for link,title, description in zip(links, titles, descriptions):
            yield response.follow(link, callback=self.parse_details,
                                  meta={'link': response.urljoin(link),
                                        'title': title.strip(),
                                        'description': description.strip()})

        next_page_url = self.get_next_page_url(response)
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    def parse_details(self, response):
        tag_type_map = {
            'p': 'paragraph',
            'h2': 'header',
            'h3': 'subheader',
            'li': 'list-item'
        }
        article_content = []
        content_elements = response.css('div.article-column__content *')
        # Iterate over all children and process based on their tag type
        for element in content_elements:
            tag = element.root.tag  # Get the tag name of the element
            html_content = element.get()  # Get the HTML content of the element
            text = self.clean_html(html_content)  # Clean HTML tags and get text

            if text and self.contains_ontology_term(text, self.ontology_terms):
                if tag in tag_type_map:
                    article_content.append({'type': tag_type_map[tag], 'text': text})

        # Combine all data and yield it
        yield {
            'link': response.meta['link'],
            'title': response.meta['title'],
            'description': response.meta['description'],
            'article_content': article_content
        }

    def clean_html(self, html_content):
        # Use BeautifulSoup to clean HTML tags and content
        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.get_text(separator=' ', strip=True)
        # Check if the text is empty or consists only of whitespace
        if text:
            return text
        return None  # Return None if the paragraph is empty or contains only whitespace

    def contains_ontology_term(self, text, terms):
        text_lower = text.lower()
        return any(term in text_lower for term in terms)

    def get_next_page_url(self, response):
        # Try to identify the next page link by its unique structure
        next_page_link = response.css('nav.pagination a.next.pagination__link::attr(href)').get()
        return next_page_link