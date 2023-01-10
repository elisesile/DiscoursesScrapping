import csv
import requests
from bs4 import BeautifulSoup, element
import datetime

class SpeechFetcher():

    def __init__(self, name, minDate=datetime.datetime(2022,1,1)):
        """
        ARGUMENTS:
            name : string = name of the person whose speeches are to be fetched
            minDate : datetime.datetime = date for further back discourse fetched 
        """
        self.url = "https://www.vie-publique.fr/discours/recherche?search_api_fulltext_discours=&sort_by=field_date_prononciation_discour&field_intervenant_title=" + name + "&field_intervenant_qualite=&field_date_prononciation_discour_interval[min]=&field_date_prononciation_discour_interval[max]=&form_build_id=form-QSFeXpZlrul8WOdhDjKDD4D7cJY4sWEWf57JVngxYfw&form_id=views_exposed_form&page="
        
        self.minDate = minDate

    def fetching(self):

        date = datetime.datetime.today()
        i = 0 
        speeches = []

        while date > self.minDate :

            page = requests.get(self.url + str(i)) # Getting page HTML through request
            soup = BeautifulSoup(page.content, 'html.parser')
            results = soup.select('div.views-row')
        
            for speech_num in range(len(results)):

                speech = {}
                speech['url'] = "https://www.vie-publique.fr" + results[speech_num].select_one("a").attrs['href']
                speech['date'] = datetime.datetime.strptime(results[speech_num].time.attrs['datetime'][:10], "%Y-%m-%d")
                speech['speaker'] = results[speech_num].select("a")[1].get_text()
                speech['title'] = results[speech_num].select_one("a").get_text()

                sp_content = requests.get(speech['url'])
                sp_content = BeautifulSoup(sp_content.content, "html.parser")
    
                try :

                    if date < datetime.datetime(2019,1,1):
                        try :
                            speech['content'] = sp_content.select_one('span.clearfix').get_text().encode('latin1').decode('windows-1252').replace('\xa0', ' ')
                        except UnicodeEncodeError :
                            speech['content'] = sp_content.select_one('span.clearfix').get_text()
                    else:
                        speech['content'] = " ".join([ content.get_text().replace('\xa0', ' ') for content in sp_content.select('div.discour--desc span.clearfix p')])

                    speeches.append(speech)
                    
                except Exception:
                    print(speech['title'], speech['url'])

                date = speech['date']

            print("Processed speeches N°", 10*i, ' to N°', 10*(i+1))
            i += 1

        self.speeches = speeches

        return speeches

    def csv_export(self, filename):

        with open(filename + '.csv', 'w', newline='') as csvfile:
            
            fieldnames = ['url','date','speaker','title','content']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for speech in self.speeches :
                writer.writerow(speech)