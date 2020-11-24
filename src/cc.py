"""Closed caption processing"""

from youtube_transcript_api import YouTubeTranscriptApi as yttapi
# https://github.com/jdepoix/youtube-transcript-api
import spacy
# https://spacy.io/usage/linguistic-features
# https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz
from collections import Counter
from random import choice

IGNORETAGS = ["ADP", "AUX", "CONJ", "PART", "PUNCT", "SCONJ", "SYM", "X", "SPACE"]

class contextStruct:
    interjections = []
    adjectives = []
    nouns = []
    adverbs = []
    verbs = []
    determiners = []
    def __init__(self, validTokens):
        interjections = mostFrequentWords(validTokens, "INTJ")
        adjectives = mostFrequentWords(validTokens, "ADJ")
        nouns = mostFrequentWords(validTokens, "NOUN")
        nouns += mostFrequentWords(validTokens, "PROPN")
        adverbs = mostFrequentWords(validTokens, "ADV")
        verbs = mostFrequentWords(validTokens, "VERB")
        determiners = mostFrequentWords(validTokens, "DET")
        # take care of default values
        self.interjections = interjections if len(interjections) > 0 else ["wow", "haha"]
        self.adjectives = adjectives if len(adjectives) > 0 else ["interesting", "funny", "ordinary", "controversial", "painstaking"]
        self.nouns = nouns if len(nouns) > 0 else ["person", "thing"]
        self.adverbs = adverbs if len(adverbs) > 0 else ["quickly", "slowly"]
        self.verbs = verbs if len(verbs) > 0 else ["did", "threw", "took", "said"]
        self.determiners = determiners if len(determiners) > 0 else ["the", "that", "this", "these"]


sentenceStructures = [
    "DET ADJ NOUN VERB.",
    "DET NOUN ADV VERB.",
    "DET NOUN VERB...",
    "INTJ! INTJ!!",
    "INTJ! NOUN VERB DET ADJ NOUN, ADV.",
    "INTJ, DET NOUN VERB NOUN.",
    "NOUN ADV VERB NOUN ADV.",
    "NOUN ADV VERB NOUN!",
    "NOUN VERB DET ADJ NOUN ADV.",
    "DET ADJ NOUN VERB.",
    "DET NOUN VERB DET ADJ NOUN ADV, INTJ!",
    "INTJ. DET NOUN VERB.",
    "NOUN VERB!",
    "INTJ, INTJ, INTJ. NOUN ADV VERB NOUN."
]

def fetchTranscript(videoID):
    return yttapi.get_transcript(videoID)

def fetchTranscriptRaw(transcript):
    return " ".join([i["text"] for i in transcript]).lower()

def fetchIntervalRaw(transcript, a, b):
    return fetchTranscriptRaw(fetchInterval(transcript, a, b))

def fetchInterval(transcript, a, b):
    thisTranscript = []
    for t in transcript:
        if (t["start"] + 5 >= a) and (t["start"] + t["duration"] - 5 <= b):
            thisTranscript.append(t)
    return thisTranscript

def determineContext(transcriptRaw):
    global IGNORETAGS
    sentence = ""
    nlp = spacy.load("en_core_web_sm")
    tokenized = nlp(transcriptRaw)
    validTokens = [token for token in tokenized if token.pos_ not in IGNORETAGS]
    context = contextStruct(validTokens)
    return constructSentence(context)

def constructSentence(context):
    if type(context) != contextStruct: raise TypeError("contextStruct expected")
    w = lambda words: choice(words)
    j = int(len(context.nouns) * .5)
    if j == 0:
        return ""
    sentences = []
    while j > 0:
        sentence = choice(sentenceStructures)
        while any(tag in sentence for tag in ["INTJ", "ADJ", "NOUN", "ADV", "VERB", "DET"]):
            sentence = sentence.replace("INTJ", w(context.interjections), 1)
            sentence = sentence.replace("ADJ", w(context.adjectives), 1)
            sentence = sentence.replace("NOUN", w(context.nouns), 1)
            sentence = sentence.replace("ADV", w(context.adverbs), 1)
            sentence = sentence.replace("VERB", w(context.verbs), 1)
            sentence = sentence.replace("DET", w(context.determiners), 1)
        sentences.append(sentence.capitalize())
        j -= 1
    return choice(sentences)

def mostFrequentWords(validTokens, pos):
    counter = Counter([ token.text for token in validTokens if token.pos_ == pos ])
    count = int(len(counter) * .5) + 1
    freqWords = [i[0] for i in counter.most_common(count)]
    return freqWords

def getNouns(sentence):
    nlp = spacy.load("en_core_web_sm")
    tokenized = nlp(sentence)
    return [token.text for token in tokenized if token.pos_ == "NOUN"]

# [
#     {
#         'text': 'Hey there',
#         'start': 7.58,
#         'duration': 6.13
#     },
#     {
#         'text': 'how are you',
#         'start': 14.08,
#         'duration': 7.58
#     },
#     # ...
# ]
