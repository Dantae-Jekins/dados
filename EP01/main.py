import scrapy
import re
import requests
from scrapy.selector import Selector

#scrapy runspider main.py -o saida.json
#scrapy runspider main.py -o saida.csv
#scrapy runspider --nolog main.py


class BlogSpider(scrapy.Spider):
  #print("aaaaa")
  name = 'blogspider'
  meta = 'ac'
  start_urls = ['https://pokemondb.net/pokedex/all']

  def parse(self, response):
    limit = 0
    for pokemon in response.css('table#pokedex > tbody > tr'):
      limit+= 1
      if limit > 11:
        break
      url_select = pokemon.css('td:nth-child(2) > a::attr(href)')
      yield response.follow(
          url_select.get(),
          self.parse_bicho,
      )

  def parse_bicho(self, resp):
    name = resp.css('#main > h1::text').get()
    peso = resp.css('div:nth-child(1) > div:nth-child(2) > table > tbody > tr:nth-child(5) > td::text').get()
    altura = resp.css('div:nth-child(1) > div:nth-child(2) > table > tbody > tr:nth-child(4) > td::text').get()
    id = resp.css('div:nth-child(1) > div:nth-child(2) > table > tbody > tr:nth-child(1) > td > strong::text').get()
    type = set(resp.css('div:nth-child(1) > div:nth-child(2) > table > tbody > tr:nth-child(2) > td > a::text').getall())
    abilitiesurl = resp.css('div:nth-child(1) > div:nth-child(2) > table > tbody > tr:nth-child(6) > td > * > a::attr(href)').getall()
    evolutions = resp.css('#main > div.infocard-list-evo > * > span:nth-child(2) > a::text').getall()
    abilities = self.parse_ability(abilitiesurl)
    
    nextevolution = None
    for i in range(0, len(evolutions)):
      if evolutions[i] == name:
        nextevolution = None if i == (len(evolutions) - 1) else evolutions[i +1:]

    yield {
        'id': id,
        'name': name,
        'type': type,
        'weight': peso,
        'height': altura,
        'abilities': abilities,
        'evolutions': nextevolution
    }
  def parse_ability(self, abilitiesurl):
    descriptions = []
    for url in abilitiesurl:
      r = requests.get("https://pokemondb.net"+url)
      body = r.text
      abilityName = Selector(text=body).css("#main > h1::text").get()
      abilityDesc = Selector(text=body).css("div.grid-col:nth-child(1) > p").get()
      abilityDescParsed = "".join(re.sub('(<[^>]*?>)', "", abilityDesc))  
      descriptions.append({"abilityname" : abilityName, "abilitydesc" : abilityDescParsed, "abilityurl":url})
    return descriptions

