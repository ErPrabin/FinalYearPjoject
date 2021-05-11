import random
import json
import torch
from model import NeuralNet
from tokenizationAndStemming import BagOfWords, tokenize
from voice import listener
import dominate
import pyttsx3
import os.path

from dominate.tags import *
engine = pyttsx3.init()
engine.setProperty('rate', 130)

from specialHandlers import handleSrc, handleTable, handleList, handleSelect

# Tokenize, stem the spoken word and shape them to fit on the model


def tokenizeAndStemSpoken(sentence, allWords):
    sentence = tokenize(sentence)
    x = BagOfWords(sentence, allWords)
    x = x.reshape(1, x.shape[0])
    x = torch.from_numpy(x)
    return x


# open the intents file
with open("intents.json", "r") as f:
    intents = json.load(f)
with open("attributes.json", "r") as f:
    attributes = json.load(f)

# Load the creadential saved during training

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
# synthesize next Html tag or attribute provided


def synthesizeTag(sentence, botName, recType):
    # load the statedictionary
    model.load_state_dict(modelState)
    model.eval()

    # tokenize find BOG predict the class for new sentence
    x = tokenizeAndStemSpoken(sentence, allWords)

    # find the predicted output
    output = model(x)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    # apply softmax to find probability of predicted class
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    # loop for pattern to see if any pattern matches
    if prob.item() > 0.85:
        # now we have to decide are we looking for tag or attribute
        if recType == 1:
            for intent in intents['intents']:
                if tag == intent["tags"]:
                    return tag
        else:
            for attribute in attributes['attributes']:
                if tag == attribute['attr']:
                    return tag
    else:
        engine.say('I do not understand')
        engine.runAndWait()


        print(f"{botName}: I do not understand...")

# listen to user for tag or atrribute


def listenUser(recType):
    # dont be confuse this while is for the case when tag is not recognized
    while True:
        # create the bot
        botName = "Jony"
        if recType == 1:
            engine.say('Lets hear tag')
            engine.runAndWait()

            print("Let's hear tag!")
        else:
            engine.say('Lets hear tag')
            print("Let's hear atriibute! ")

        # listen to voice command
        sentence = listener()
        engine.say('I hear')
        # engine.say(sentence)
        # engine.runAndWait()


        print('Jony: I hear>', sentence)

        # see if the user say quit to end the tag
        if 'quit' in sentence:
            return 'quit'
        elif 'finish' in sentence:
            return 'quit'
        else:
            print(f'you: {sentence}')
            # if command is understandable synthesize the tag
            tag = synthesizeTag(sentence, botName, recType)
            print(f'jony: {tag}')
            return tag


def listenTag():
    # listen the tag
    innerElement = []
    tag = listenUser(1)
    # we have to handle some special tag like tabe,list,inputoption etc
    if tag == 'table':
        innerElement = handleTable()
    if tag == 'ol' or tag == 'ul':
        innerElement = handleList()
    if tag == "form":
        innerElement = handleForm()
    if tag == 'select':
        innerElement = handleSelect()

    return tag, innerElement

# it listen to the attribute for special tag


def listenAttribute(tag):
    attribute = []
    # For each tag there can be multiple attributes listen to the attributes
    while True:
        listenedAttribute = listenUser(2)
        if listenedAttribute is not None:
            if 'quit' in listenedAttribute:
                return attribute
            # we have to handle some special attribute like src,values of option
            if listenedAttribute == "src":
                value = handleSrc()
            else:
                print(f'jony: speak {listenedAttribute} value')
                value = listener()
            attrValue = {
                "attr": listenedAttribute,
                "value": value
            }
            attribute.append(attrValue)


def completeListener():
    # empty lists to contain the atriibute and
    tag = []
    attribute = []
    innerElement = []
    innerText = []

    # listen to various tag and their inner nested tags
    tag, innerElement = listenTag()

    # some tag like img,vedio,input,href need atrribute like src,type,href
    mustHaveAtrribute = ['img', 'input', 'vedio', 'a']

    # listen to associated attribute
    if tag in mustHaveAtrribute:
        attribute = listenAttribute(tag)

    # now we have to listen to the innertext if there is any
        

    engine.say('Is there any inner text associated say yes to have it')
    engine.runAndWait()
    print(
        f'is there any inner text associated with {tag} ? ... Say "Yes" to have it..')
    openion = listener()
    if 'yes' in openion:
        innerText = listener()

    # After tag and attributes are clear make appropriate data to pass to react
    data = {
        "element": tag,
        "innerText": innerText,
        "attributes": attribute,
        "innerElement": innerElement
    }
    return data


def handleForm():
    tags = []

    while True:
        tag = completeListener()
        tags.append(tag)
        engine.say('Is there more tag inside form')
        engine.runAndWait()


        print('is there more tag inside form?')
        engine.say('Till now')
        engine.runAndWait()


        print('till now ', tags)
        openion = listener()
        if 'yes' not in openion:
            return tags


# dictionary to hold the command given
commandTags = {
    "tags": []
}


def main():
    # listen to user, predict the command, and gve appropriate response
    data = completeListener()

    # save the command to dictionary
    commandTags["tags"].append(data)

    print("commandTags:", commandTags)

    if os.path.isfile('main_index.html'):
        print('file exist')

    else:
        file_object = open('main_index.html', 'a')
        file_object.write('<html lang="en"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" /><script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script><script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script><title>Document</title></head><body><div class="container"> ')
        file_object.close()


    # doc = dominate.document(title='Dominate your HTML')
    for tag in commandTags['tags']:
        print(tag['element'], tag['innerText'])
        if(tag['element'] == 'p'):
            file_object = open('main_index.html', 'a')
            file_object.write('<p>'+tag['innerText']+'</p>'+'<br>')
            file_object.close()
        elif(tag['element'] == 'button'):
            file_object = open('main_index.html', 'a')
            file_object.write('<button class="btn btn-primary">'+tag['innerText']+'</button>'+'<br>')
            file_object.close()
        elif(tag['element'] == 'header'):
            file_object = open('main_index.html', 'a')
            file_object.write('<h1>'+tag['innerText']+'</h1>'+'<br>')
            file_object.close()
        elif(tag['element'] == 'sub_header'):
            file_object = open('main_index.html', 'a')
            file_object.write('<h3>'+tag['innerText']+'</h3>'+'<br>')
            file_object.close()
        elif(tag['element'] == 'anchor'):
            file_object = open('main_index.html', 'a')
            file_object.write('<a>'+tag['innerText']+'</a>'+'<br>')
            file_object.close()
        elif(tag['element'] == 'ol'):
            file_object = open('main_index.html', 'a')
            file_object.write('<ol>')
            file_object.close()
            
            for data in tag['innerElement']:
                # print(data['value'])
                file_object = open('main_index.html', 'a')
                file_object.write('<li style="line-height: 50px;background-color: black;color: white;font-size: 24px;width: 50%;padding-left: 50px;">'+data['value']+'</li>')
                file_object.close()

            file_object = open('main_index.html', 'a')
            file_object.write('</ol>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'ul'):
            file_object = open('main_index.html', 'a')
            file_object.write('<ul>')
            file_object.close()
            
            for data in tag['innerElement']:
                # print(data['value'])
                file_object = open('main_index.html', 'a')
                file_object.write('<li style="line-height: 50px;background-color: black;color: white;font-size: 24px;width: 50%;padding-left: 50px;">'+data['value']+'</li>')
                file_object.close()

            file_object = open('main_index.html', 'a')
            file_object.write('</ul>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'form'):
            file_object = open('main_index.html', 'a')
            file_object.write('<form>')
            file_object.close()
            
            for data in tag['innerElement']:
                # print(data['value'])
                file_object = open('main_index.html', 'a')
                if(data['element']=='label'):
                 file_object.write('<label style="font-size: 16px;width: 100%;">'+data['innerText']+'</label>'+'<br>')
                elif(data['element']=='input'):
                    for inputdata in data['attributes']:
                        file_object.write('<input style="font-size: 16px;width: 100%;"'+'type="'+inputdata['value']+'"'+'<br>')
                file_object.close()

            file_object = open('main_index.html', 'a')
            file_object.write('</form>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'li'):
            file_object = open('main_index.html', 'a')
            file_object.write('<li style="line-height: 50px;background-color: black;color: white;font-size: 24px;width: 50%;padding-left: 50px;">'+tag['innerText']+'</li>')
            file_object.close()

        elif(tag['element'] == 'select'):
            file_object = open('main_index.html', 'a')
            file_object.write('<select style="width: 50%;height: 50px;font-size: 20px;padding-left: 50px;">')
            file_object.close()
            
            for data in tag['innerElement']:
                # print(data['value'])
                file_object = open('main_index.html', 'a')
                file_object.write('<option>'+data['value']+'</option>')
                file_object.close()

            file_object = open('main_index.html', 'a')
            file_object.write('</select>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'table'):
            file_object = open('main_index.html', 'a')
            file_object.write('<table style="font-family: arial, sans-serif;border-collapse: collapse;width: 100%;">')
            file_object.close()
            
            for data in tag['innerElement']:
                val=1
                file_object = open('main_index.html', 'a')
                file_object.write('<tr>')
                file_object.close()

                if(val==1):
                    for tabledata in data['innerElement']:
                        file_object = open('main_index.html', 'a')
                        file_object.write('<th style="border: 1px solid #dddddd;text-align: left;padding: 8px;">'+tabledata['value']+'</th>')
                        file_object.close()
                        val=2
                elif(val>1):
                    for tabledata in data['innerElement']:
                        file_object = open('main_index.html', 'a')
                        file_object.write('<td style="border: 1px solid #dddddd;text-align: left;padding: 8px;">'+tabledata['value']+'</td>')
                        file_object.close()
                        val=2

            file_object = open('main_index.html', 'a')
            file_object.write('</tr>')
            file_object.close()

            file_object = open('main_index.html', 'a')
            file_object.write('</table>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'caption'):
            file_object = open('main_index.html', 'a')
            file_object.write('<caption>'+tag['innerText']+'</caption>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'img'):
            for data in tag['attributes']:
                # for imagedata in
                file_object = open('main_index.html', 'a')
                file_object.write('<img style="width:100%;height:400px;" '+'src="'+'F:\FinalYear_Project\imgAndVedio/'+data['value']+'"'+'>'+'</img>'+'<br>')
                file_object.close()

        elif(tag['element'] == 'i'):
            file_object = open('main_index.html', 'a')
            file_object.write('<i>'+tag['innerText']+'</i>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'strong'):
            file_object = open('main_index.html', 'a')
            file_object.write('<strong>'+tag['innerText']+'</strong>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'b'):
            file_object = open('main_index.html', 'a')
            file_object.write('<b>'+tag['innerText']+'</b>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'dialog'):
            file_object = open('main_index.html', 'a')
            file_object.write('<dialog open>'+tag['innerText']+'</dialog>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'textarea'):
            file_object = open('main_index.html', 'a')
            file_object.write('<textarea style="width: 100%;height: 30%;">'+tag['innerText']+'</textarea>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'fieldset'):
            file_object = open('main_index.html', 'a')
            file_object.write('<fieldset>'+tag['innerText']+'</fieldset>'+'<br>')
            file_object.close()
        elif(tag['element'] == 'br'):
            file_object = open('main_index.html', 'a')
            file_object.write('<br>')
            file_object.close()

        elif(tag['element'] == 'hr'):
            file_object = open('main_index.html', 'a')
            file_object.write('<hr style="border-top: 5px solid #eee;">'+'<br>')
            file_object.close()

        elif(tag['element'] == 'address'):
            file_object = open('main_index.html', 'a')
            file_object.write('<address>'+tag['innerText']+'</address>'+'<br>')
            file_object.close()

        elif(tag['element'] == 'footer'):
            file_object = open('main_index.html', 'a')
            file_object.write('<footer style="background-color: gray;">')
            file_object.write('<p>'+tag['innerText']+'</p>'+'<br>')
            file_object.write('<a href="mailto:ersolution22@gmail.com">'+'ersolution22@gmail.com'+'</a>'+'<br>')
            file_object.write('</footer>'+'<br>'+'<br>')
            file_object.close()


if __name__ == "__main__":
    main()
