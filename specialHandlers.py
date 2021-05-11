from pathlib import Path
from voice import listener
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 130)
#from implementMain import completeListener


def handleSrc():
    while True:
        print(f'jony: speak src value')
        spoken = listener()
        # file are with different extension like .jpg,jpeg,mp4 we have to find appropriate file
        fileToOpen = completeFile(spoken)
        if fileToOpen:
            return fileToOpen


def handleTable():
    row = 1
    rowData = []
    while True:
        print(f'Table row {row}')
        rowInner = listenTableData(row)
        intermidiateRow = {
            "tag": 'tr',
            "innerElement": rowInner
        }
        rowData.append(intermidiateRow)
        print(rowData)
        engine.say('Want to add more rows say yes to add it')
        engine.runAndWait()
        
        print(f"want to add more rows? 'Yes' to continue")
        openion = listener()
        if "yes" not in openion.lower():
            return rowData
        row = row+1


def listenTableData(row):
    tag = 'td'
    values = []
    if row == 1:
        tag = 'th'
    # now to listen data in a table row we loop
    while True:
        engine.say('Give me a data.')
        engine.runAndWait()
        print(f"speak {tag} data")
        spoken = listener()
        data = {
            "tag": tag,
            "value": spoken
        }
        values.append(data)
        engine.say('Is there more table data say yes to have it')
        engine.runAndWait()
        print(f"more {tag}? speak 'Yes' to continue")
        openion = listener()
        if "yes" not in openion.lower():
            return values

# this handle specially ordered or unordered list


def handleList():
    listNo = 1
    listCollection = []
    while True:
        engine.say('Give me a list value')
        engine.runAndWait()
        print(f"{listNo} list value")
        value = listener()
        list = {
            "tag": "li",
            "value": value
        }
        listCollection.append(list)
        print(f'updatedli: {listCollection} ')
        engine.say('Do you want to add more sir please say yes to continue')
        engine.runAndWait()
        print(f"want to add more? 'Yes' to continue")
        openion = listener()
        if "yes" not in openion.lower():
            return listCollection
        listNo = listNo+1

# select tag handler


def handleSelect():
    optionNo = 1
    options = []
    while True:
        engine.say('Please give me an option')
        engine.runAndWait()
        print(f"speak option {optionNo}")
        value = listener()
        option = {
            "tag": 'option',
            "value": value
        }
        options.append(option)
        print(options)
        engine.say('Is there more option sir say yes to add more')
        engine.runAndWait()
        print(f"is their more option?.. say yes to add more")
        openion = listener()
        if 'yes' not in openion.lower():
            return options
        optionNo += 1

 # this function looks for appropriate match for spekon file


def completeFile(spoken):
    dataFolder = Path(
        'F:\FinalYear_Project\imgAndVedio')
    extension = ['jpeg', 'jpg', 'png', 'mp4', 'mp3']
    print(spoken)
    if spoken.endswith('.*'):
        possible = dataFolder/spoken
        if possible.exists():
            return possible
    else:
        for complete in extension:
            imagename=(spoken+'.'+complete)
            possible = dataFolder/(spoken+'.'+complete)
            if possible.exists():
                return imagename
    engine.say('Provided File doesnot exist sir')
    engine.runAndWait()
    print("File doesn't exist")
    return None
