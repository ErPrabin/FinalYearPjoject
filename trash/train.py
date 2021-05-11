import json
import numpy
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tokenizationAndStemming import tokenize, stem, BagOfWords

# import voice
from model import NeuralNet


# Train the model


# Open the json file in read mode
# with open('intents.json', 'r') as f:
#     intents = json.load(f)
with open('intents.json', 'r') as f:
    intents = json.load(f)


# Tokenize and stem the pattern and tags
allWords = []
tags = []
collection = []
for intent in intents['intents']:
    tag = intent['tags']
    tags.append(tag)
    for pattern in intent['patterns']:
        words = tokenize(pattern)
        allWords.extend(words)
        collection.append((words, tag))
ignoreWords = ['?', ';', ',', '.', '!']

allWords = [stem(w) for w in allWords if w not in ignoreWords]
allWords = sorted(set(allWords))
tags = sorted(set(tags))

xTrain = []
yTrain = []

# Find out the bag of words of pattern and tags
for (patternSentence, tag) in collection:
    bag = BagOfWords(patternSentence, allWords)
    xTrain.append(bag)
    label = tags.index(tag)
    yTrain.append(label)

# Develop training data as array
xTrain = numpy.array(xTrain)
yTrain = numpy.array(yTrain)
yTrain = torch.tensor(yTrain, dtype=torch.long)

# Create new data set


class ChatDataset(Dataset):
    def __init__(self):
        self.nSample = len(xTrain)
        self.xData = xTrain
        self.yData = yTrain

    def __getitem__(self, index):
        return self.xData[index], self.yData[index]

    def __len__(self):
        return self.nSample


# Hyperparameters
batchSize = 8
# input size is same as bagof words and xTrain contain bagofwords at each row
inputSize = len(xTrain[0])
hiddenSize = 8
outputSize = len(tags)
learningRate = 0.001
numEpoch = 1000


dataSet = ChatDataset()
trainLoader = DataLoader(
    dataset=dataSet, batch_size=batchSize, shuffle=True)

# check wether we have GPU or not if yes use it
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# build the model
model = NeuralNet(inputSize, hiddenSize, outputSize)

#loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learningRate)

# start the trainning loop
for epoch in range(numEpoch):
    for (words, label) in trainLoader:

        # forward pass
        outputs = model(words)
        loss = criterion(outputs, label)

        # backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    if(epoch+1) % 100 == 0:
        print(f'epoch {epoch+1}/{numEpoch},loss = {loss.item():.4f} ')

# print the final loss
print(f'final ::loss = {loss.item():.4f} ')

# save the model
data = {
    "modelState": model.state_dict(),
    "input_size": inputSize,
    "output_size": outputSize,
    "hidden_size": hiddenSize,
    "allWords_size": allWords,
    "tags": tags,
}

FILE = "data.pth"
torch.save(data, FILE)
print(f'training complete. file saved to {FILE}')


'''
# listen to the voice and convert to text

spokenText = voice.listener()
print(spokenText)
# tokenization
# convert word to lower case and stemming
# exclude puctuation
# find out the nessecary command
# create and update the json file
# end the voice command session
# make HTML file according to json file formed
# render the HTML file thus created
# now continue the steps
'''
