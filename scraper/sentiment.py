from django.core.management.base import BaseCommand
from textblob import TextBlob
from math import log,exp
from .models import Review, Product

class Analyse(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('PID', type=str)

    def handle(self, *args, **options):
        self.PID = options['PID']
        self.predictRating()

    def getRating(self):
        try:
            return Product.objects.get(PID=self.PID).rating
        except:
            return 0

    def _sigmoidal(self,value):
        retval = ( 1 + exp(-value))**-1
        return retval

    def _sentimentFactor(self,up,down):
        try:
            normalize = log(int(up)-int(down),10)
            return self._sigmoidal(normalize)
        except:
            return 0

    def averageSentiment(self):
        retval = []
        for review in Review.objects.filter(PID=self.PID):
            try:
                string  =  str(review.heading)+' '+str(review.review)
                sentiment = TextBlob(string).sentiment.polarity
                print(sentiment)
                factor = self._sentimentFactor(review.up,review.down)
                retval.append(sentiment + sentiment*factor)
            except:
                pass
        try:
            return sum(retval)/len(retval)
        except:
            return 0

    def predictRating(self):
        at_10 = self.averageSentiment()     #at_10=sum(retval)/len(retval)
        to_5 = at_10*5                      #0<=at_10<=1
        
        if at_10 == 0:                      #NLP rating generated from reviews=0
            to_5 = self.getRating()         #no reviews  to_5=only ratings on the product
        rating = self.getRating()           #if reviews, actual rating -> rating
        print("Results--------")
        print("Flipkart Rating Out of 5: " + str(rating))
        print("Customer Reviews NLP Rating: "+str(to_5) )
        print("Average: " +str((to_5+rating)/2))
        if rating == 0:                     #Actual rating=0
            return to_5
        else:
            return (to_5+rating)/2