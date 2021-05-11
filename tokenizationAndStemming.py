from nltk.stem.porter import PorterStemmer
import nltk
import numpy as np
# nltk.download('punkt')  # It contains pretrained tokenizer

stemmer = PorterStemmer()


def tokenize(sentence):
    return nltk.word_tokenize(sentence)


def stem(word):
    return stemmer.stem(word.lower())


def BagOfWords(tokenizedWords, allWords):
    tokenizedWords = [stem(w) for w in tokenizedWords]
    allWords = [stem(w) for w in allWords]
    bag = np.zeros(len(allWords), dtype=np.float32)
    for (index, words) in enumerate(allWords):
        if words in tokenizedWords:
            bag[index] = 1.0
    return bag
