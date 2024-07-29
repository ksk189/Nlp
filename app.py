from flask import Flask, render_template, request
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load the spacy model
nlp = spacy.load('en_core_web_sm')

def summarize_text(text):
    doc = nlp(text)
    stopwords = list(STOP_WORDS)
    punctuation_set = set(punctuation + '\n')
    
    word_frequencies = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation_set:
            if word.text not in word_frequencies:
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1

    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    sentence_scores = {}
    sentence_tokens = [sent for sent in doc.sents]
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]

    select_length = int(len(sentence_tokens) * 0.3)
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)
    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)
    return summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        text = request.form['text']
        summary = summarize_text(text)
        return render_template('index.html', summary=summary, original_text=text)
    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        return render_template('index.html', error="An error occurred during summarization.")

if __name__ == '__main__':
    app.run(debug=True)