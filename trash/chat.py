import random
import json
import torch
from model import NeuralNet
from tokenizationAndStemming import BagOfWords, tokenize
from voice import listener

# open the intents file
with open("intents.json", "r") as f:
    intents = json.load(f)
FILE = "data.pth"

data = torch.load(FILE)

# load all the saved values
inputSize = data["input_size"]
outputSize = data["output_size"]
hiddenSize = data["hidden_size"]
allWords = data["allWords_size"]
tags = data["tags"]
modelState = data["modelState"]

model = NeuralNet(inputSize, hiddenSize, outputSize)

# load the state dic
model.load_state_dict(modelState)
model.eval()

# create the bot
botName = "Jony"
print("Let's chat! type quit to exit ")


def giveResponse(sentence):
    # predict the class for new sentence
    sentence = tokenize(sentence)
    x = BagOfWords(sentence, allWords)
    x = x.reshape(1, x.shape[0])
    x = torch.from_numpy(x)

    # find the predicted output
    output = model(x)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    # apply softmax to find probability of predicted class
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    # loop for pattern to see if any pattern matches
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tags"]:
                # {random.choice(intent['tags'])}
                print(f"{botName}: {tag} \n => {prob.item()} ")
    else:
        print(f"{botName}: I do not understand...")


while True:
    sentence = listener()

    # check if listener return an error
    if 'error!' in sentence:
        print(f"{botName}: I do not understand...")

    else:
        print(f'you: {sentence}')  # sentence =input('you:')
        if sentence == 'quit':
            break
        giveResponse(sentence)

        # create a json file
        file = open("websitedata.txt", "a+")
        file.write('this is the line')
        file.close()
