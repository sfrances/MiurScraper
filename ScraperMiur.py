from selenium import webdriver
import re
import json
from pprint import pprint

from bs4 import BeautifulSoup
class scraper:
    
    writeGraphite = False

    def __init__(self, simulate, WEBPAGE):    
        self.webpage = WEBPAGE
        if not simulate:
            op = webdriver.FirefoxOptions()
            op.add_argument("--headless")        
            self.driver = webdriver.Firefox(options=op)
            print("Firefox instance started...")
        else:
            print("Running in simulation mode")
        self.page = ""
        
    def GetPageContent(self):
        if not simulate:
            self.driver.get(self.webpage)
            self.driver.implicitly_wait(2)        
            try:
                html = self.driver.page_source
                #print(html)
                ### Update local file
                with open("content.html",'w') as outf:
                    outf.write(html)    
            except Exception as exc:
                print("catched into error, skip this call")
                raise(exc)
        else:
            with open("content.html","r") as inF:
                html = inF.read()
        self.page = html

    def ScrapeHtml(self):
        if len(self.page)==0:
            print("HTML output seems to be of lenght 0, exiting")
            exit(1)

        box=""
        for line in self.page.splitlines():
            
            if "Risultato della ricerca bandi" in line:
                box=line
                parsed_html = BeautifulSoup(box,features="html.parser")                
                print(parsed_html.text)
                box=""
            if "<p>" in line:
                box=""
                box+=(line)+"\n"
            if len(box)>0:
                box+=(line)+"\n"
                if "</p>" in line:
                    ### If this point is reached the <p></p> box is saved
                    ### Then one can apply filters

                    store = False

                    ### Primo check, voglio solo i bandi
                    if ('aperto' in box) or ('scaduto' in box):
                        store = True

                    ### Va migliorato, non sempre c'è FIS/01 e poi è interessa
                    # if not "FIS/01" in box:
                    #     store = False
                        
                    # if not "RTT" in box:
                    #     store = False
                        
                    if store:                        
                        parsed_html = BeautifulSoup(box,features="html.parser")                
                        outtext = parsed_html.text.replace("\n"," ")
                        links = parsed_html.find_all('a',href=True)
                        if len(links)==0:
                            url = None
                        elif len(links)==1:
                            url = "https://bandi.mur.gov.it/" + links[0]['href']
                        outtext+=" " + url
                        print(outtext)
                    ### Reset box
                    box=""
            
                    
if __name__ == "__main__":

    simulate = False


    ### All available institutes are kept in this json file
    with open('institutes.json') as iff:
        institutes = json.load(iff)

    
    institute = 'ROMA1'
    #institute = 'UNIPI'
    WEBPAGE = "https://bandi.mur.gov.it/jobs.php/public/cercaJobs?jv_comp_status_id=*&bb_type_code="+institute+"&azione=cerca&orderby=scadenza_desc"
    scraper = scraper(simulate, WEBPAGE )
    scraper.GetPageContent()
    scraper.ScrapeHtml()
    #scraper.OpenDashboard()
