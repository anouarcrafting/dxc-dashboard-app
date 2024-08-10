# # %%
# import torch
# import torch.nn as nn

# # %%
# class chatbot_nn(nn.Module):
#     def __init__(self, input_size,hidden_size,num_classes):
#         super(chatbot_nn,self).__init__()
#         self.l1=nn.Linear(input_size,hidden_size)
        
#         self.l2=nn.Linear(hidden_size,hidden_size)
#         self.l3=nn.Linear(hidden_size,num_classes)
#         self.relu=nn.ReLU()
#     def forward(self,x):
#         output=self.l1(x)
#         output=self.relu(output)
#         output=self.l2(output)
#         output=self.relu(output)
#         output=self.l3(output)
#         return output

# %%
from flair.models import TextClassifier
classifier = TextClassifier.load('en-sentiment')
# Import flair Sentence to process input text
from flair.data import Sentence
# Import accuracy_score to check performance
from sklearn.metrics import accuracy_score
def pretrained_sentiment(text):
    sentence = Sentence(text)
    classifier.predict(sentence)
    score = sentence.labels[0].score
    value = sentence.labels[0].value
    return score,value

# model using spacy 
# import spacy

# nlp = spacy.load("en_core_web_sm") 
# sentiment_analyzer = nlp.create_pipe("sentiment_analyzer")

# nlp.add_pipe(sentiment_analyzer) 
# def spacy_sentiment(text):
#     sentiment = sentiment_analyzer(text)
#     return sentiment.sentiment,sentiment.score
