# Import the libraries
import json
import numpy
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from tokenizationAndStemming import tokenize, stem, BagOfWords

from model import NeuralNet

# It is a data set for facilating the data access and use


class ChatDataset(Dataset):
    def __init__(self, xTrain, yTrain):
        self.nSample = len(xTrain)
        self.xData = xTrain
        self.yData = yTrain

    def __getitem__(self, index):
        return self.xData[index], self.yData[index]

    def __len__(self):
        return self.nSample


# 2> create collection according to input
def createCollection(fName, which, name):
    allWords = []
    tags = []
    collection = []
    key = 'intents' if which == 1 else 'attributes'
    for value in fName[key]:
        tag = value[name]
        tags.append(tag)
        for pattern in value['patterns']:
            words = tokenize(pattern)
            allWords.extend(words)
            collection.append((words, tag))
    ignoreWords = ['?', ';', ',', '.', '!', '/']
    allWords = [stem(w) for w in allWords if w not in ignoreWords]
    allWords = sorted(set(allWords))
    tags = sorted(set(tags))

    return collection, allWords, tags


# main operating area of training
def main():
    # 1>#open the appropriate files
    # Open the intents.json file in read mode
    with open('intents.json', 'r') as f:
        intents = json.load(f)
    # open the attribute file as attribute
    with open('attributes.json', 'r') as p:
        attributes = json.load(p)

    # 2># create collection from both files
    collection1, allWords1, tags1 = createCollection(intents, 1, "tags")
    collection2, allWords2, tags2 = createCollection(attributes, 2, "attr")

    # 3># concatinate these to create the main collection and words
    collection1.extend(collection2)
    allWords1.extend(allWords2)
    tags1.extend(tags2)

    # 4># define xTrain and yTrain
    xTrain = []
    yTrain = []

    # 5># Find out the bag of words of pattern and tags
    for (patternSentence, tag) in collection1:
        bag = BagOfWords(patternSentence, allWords1)
        xTrain.append(bag)
        label = tags1.index(tag)
        yTrain.append(label)

    # 6># Develop training data as array
    xTrain = numpy.array(xTrain)
    yTrain = numpy.array(yTrain)
    yTrain = torch.tensor(yTrain, dtype=torch.long)

    # 7>## Hyperparameters for further training
    batchSize = 8
    # input size is same as bagof words and xTrain contain bagofwords at each row
    inputSize = len(xTrain[0])
    hiddenSize = 8
    outputSize = len(tags1)
    learningRate = 0.001
    numEpoch = 1000

    # 8># dataset and trainLoader for data loading and preparation
    dataSet = ChatDataset(xTrain, yTrain)
    trainLoader = DataLoader(
        dataset=dataSet, batch_size=batchSize, shuffle=True)

    # 9># build the model
    model = NeuralNet(inputSize, hiddenSize, outputSize)

    # 10# loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learningRate)

    # 11># start the trainning loop
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

    # save the model attributes in a file .pth extension
    data = {
        "modelState": model.state_dict(),
        "input_size": inputSize,
        "output_size": outputSize,
        "hidden_size": hiddenSize,
        "allWords_size": allWords1,
        "tags": tags1,
    }

    FILE = "data.pth"
    torch.save(data, FILE)
    print(f'training complete. file saved to {FILE}')


if __name__ == "__main__":
    main()
