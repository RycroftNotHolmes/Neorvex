from django.core.management.base import BaseCommand
from selenium import webdriver
from .models import Product, Review, Images, Prices
from requests import get
from bs4 import BeautifulSoup as bs
from pprint import pprint
from .sentiment import Analyse
import scrapy

class PhantomSource:
    def getSource(self,URL):
        driver =webdriver.PhantomJS(executable_path=r"C:\Users\jinsb\Downloads\phantomjs-2.1.1-windows\bin\phantomjs.exe")
        #driver = webdriver.PhantomJS()
        driver.get(URL)
        retval= driver.page_source
        driver.quit()
        return retval


class toDB(BaseCommand):
    prodID=""
    def add_arguments(self, parser):
        parser.add_argument('PID', type=str)
        parser.add_argument('P_name',type=str)
        parser.add_argument('rating', type=float)
        parser.add_argument('specifications', type=str)

    def handle(self, product_data):
        self.prodID = product_data['PID']

    def insertSpecs(self, product_data):
        product = Product.objects.create(
            PID=product_data['PID'],
            title=product_data['title'],
            rating=product_data.get('rating', 0),
            specifications=product_data.get('specifications', '')
        )
    
    def insertPrices(self, product_price):
        prices = Prices.objects.create(
            PID=self.prodID,
            seller=product_price['seller'],
            price=product_price['price'],
            url=product_price['url']   
        )

    def insertImages(self, product_images):
        if len(product_images)>0:
            Images.objects.create(
                PID=self.prodID,
                image1=product_images[0]
            )
            if len(product_images)>1:
                image=Images.objects.get(primary_key=self.prodID)
                image.image2=product_images[1]
                image.save()
                if len(product_images)>2:
                    image=Images.objects.get(primary_key=self.prodID)
                    image.image3=product_images[2]
                    image.save()
                    if len(product_images)>3:
                        image=Images.objects.get(primary_key=self.prodID)
                        image.image4=product_images[3]
                        image.save()
        else:
            Images.objects.create(
                PID=self.prodID
            )

    def insertReviews(self, reviews_data):
        #review_data ={'heading':i,'review':j,'PID':PID, 'up':k,'down':m}
        #reviews_data=[dic1,dic2,dic3]
        for review_data in reviews_data:
            Review.objects.create(
                PID=review_data['PID'],
                heading=review_data['heading'],
                review=review_data['review'],
                up=review_data['up'],
                down=review_data['down']
            )
            

class ScrapeFL(BaseCommand):
    globalPID=0
    URL_Base = "https://www.flipkart.com"
    def __init__(self):
        self.toDB = toDB()

    def getPID(self,string):
        try:
            start = string.index("pid=")
            end = string.index('&')
            return string[start+4:end]
        except:
            return ''

    def scrapeProduct(self,string):
        #URL=urlencode()
        URL = "https://www.flipkart.com/search?q=" + string
        soup = bs(get(URL).text)
        p_class = "_3v8VuN"
        try:
            p_no =  int(soup.find('span',{'class':p_class}).span.contents[1].split(' ')[3].replace(',',''))
        except:
            p_no = 0
        print( "Search Result Pages= "+str(p_no))
        for i in range(p_no+1):
            data = self.extractProductNames(URL+"&page="+str(i+1))
            print( '\n'.join([str(data.index(j)) + ". "+j['title'] for j in data]))
            print ("More results ? press enter. Else give index of your product.")
            #print(data[0]) //data=> title,link,pid

            inp = input()
            if ( inp == ''):
                continue
            else:
                data  = self.scrapeIndividual(data[int(inp)])
                print(data)
                break
        self.toDB.handle(data[0])
        self.toDB.insertSpecs(data[0])
        self.toDB.insertImages(data[1])
        for i in data[2]:
            self.toDB.insertReviews(i)
        predicted_rating = Analyse(self.globalPID).predictRating()
        product=Product.objects.get(primary_key=data[0]['PID'])
        product.predicted_rating=predicted_rating
        product.save()
        Review.objects.filter(PID=self.globalPID).delete()
                        
    def extractProductNames(self,URL_product):
        all_results = []
        rectify = "_2cLu-l"
        soup = bs(get(URL_product).text)
        all_results = [ {'title':i['title'],'link':self.URL_Base+i['href'],'pid':self.getPID(i['href'])} for i in soup.findAll('a',{'class':rectify}) ]

        if(all_results==[]):

            for i in soup.findAll('a',{'class':'_1UoZlX'}):
                dics = {}
                dics['link']=self.URL_Base+i['href']
                dics['pid']=self.getPID(i['href'])
                dics['title']=i.find('div',{'class':'_3wU53n'}).string
                all_results.append(dics)
        #print(all_results)

        return all_results

    def scrapeIndividual(self,Object_individual):
        #page for a particular product
        print("Product Page: " + str(Object_individual['link']))
        soup = bs(get(Object_individual['link']).text)
        PID = Object_individual['pid']
        P_name = Object_individual['title']
        in_spec_class = "_2Kp3n6"
        in_spec_name = "HoUsOy"
        key_class = "vmXPri col col-3-12"
        value_class = "sNqDog"
        review_class = "swINJg _3nrCtb"
        rating_class = "_1i0wk8"
        image_class = "_3ktMjD"
        retval = {}

        URL_review = soup.find('div',{'class':review_class}).parent['href']

        data = soup.findAll('div',{'class':in_spec_class})
        try:
            rating = soup.find('div',{'class':rating_class}).string
        except:
            rating = 0

        for i in data:
            try:
                sub_name = i.find('div',{'class':in_spec_name}).contents[0]
            except:
                sub_name = 'base_info'+str(data.index(i))
            dic = {}

            all_keys = [j.contents[0] for j in i.findAll('div',{'class':key_class})]
            all_values = [j.contents[0] for j in i.findAll('li',{'class':value_class})]

            for j,k in zip(all_keys,all_values):
                dic[j]=k
            retval[sub_name] = dic
        retval['title'] =P_name
        retval['PID'] = PID
        retval['rating'] = rating
        print("Reviews Page : "+ str(self.URL_Base+URL_review))
        
        # Scrape images
        images = []
        for img in soup.findAll('img', {'class': image_class}):
            images.append(img['src'])
        retval.append(images)
        return [retval,self.getReviews(self.URL_Base+URL_review,PID)]

    def getReviews(self,reviewURL,PID):
        retval = []
        soup = bs(PhantomSource().getSource(reviewURL))
        p_class = "_3v8VuN"
        try:
            p_no =  int(soup.find('span',{'class':p_class}).span.contents[1].split(' ')[3].replace(',',''))
        except:
            p_no = 0

        if reviewURL[reviewURL.index('?')+1:reviewURL.index('?')+5] != 'page':


            parts = reviewURL.split('?')
            print("Flipkart Product Id: "+ str(parts[1][4:]))
            self.globalPID= parts[1][4:]
        else:
            parts = reviewURL.split('?page=1')

        print("Review Pages "+str(p_no))
        if(p_no > 10 ):
            print("How many pages to scrape ?")
            p_no = input()

        for i in range(0,int(p_no)):
            URL = ('?page='+str(i+1)+"&").join(parts)
            print("Getting Reviews Of Page "+str(i+1))
            retval += self.getReviewPerPage(URL,PID)
        print("Reviewing Done")
        return retval

    def getReviewPerPage(self,reviewURL,PID):
        soup = bs(PhantomSource().getSource(reviewURL))
        box_class = "_3DCdKt"
        heading_class = "_2xg6Ul"
        review_class = "qwjRop"
        span_class = "_1_BQL8"

        blocks = soup.findAll('div',{'class':box_class})
        heading = [ i.find('p',{'class':heading_class}).string for i in blocks ]
        review =  [ i.find('div',{'class':review_class}).div.div.string for i in blocks ]
        thumbs_up = [ i.findAll('span',{'class':span_class})[0].string for i in blocks ]
        thumbs_down = [ i.findAll('span',{'class':span_class})[1].string for i in blocks ]

        retval = []

        for i,j,k,m in zip(heading,review,thumbs_up,thumbs_down):
                dic ={}
                dic['heading'] = i
                dic['review'] = j
                dic['PID'] = PID
                dic['up'] = k
                dic['down'] = m
                #dic ={'heading':i,'review':j,'PID':PID, 'up':k,'down':m}
                #retval=[dic1,dic2,dic3]
                retval.append(dic)
        return retval

    def add_arguments(self, parser):
        parser.add_argument('product', type=str)

    def handle(self, *args, **options):
        self.globalPID = options['product']
        self.scrapeProduct(self.globalPID)