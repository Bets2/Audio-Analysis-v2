from textblob import TextBlob as blob

tb = blob("Hi, please like this Vedeo")

print(tb.noun_phrases)
