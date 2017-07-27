# beer-crawl

* getBeer.py: includes two functions

	- getBeerLinks: retrieves URLs directing to beer reviews from a list
	- getBeerInfo: extracts beer review information into a dictionary

The keys used in the dictionary are
['Name', 'Appearance', 'Aroma', 'Taste', 'Palate', 'Total', 'Type', 
'Brewery', 'Pros', 'Cons', 'Conclusion', 'Alcohol', 'IBU', 'Size', 
'Date Reviewed', 'Reviewer', 'Categories', 'Tags', 'Review Text', 'URL']

* beerCrawler.py: Python script to deploy to create beer database; uses getBeer.py

* beerURLs.txt: text file containing the individual URLs for beer reviews

* beer_info.csv: csv file containing information about beers