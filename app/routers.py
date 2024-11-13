from flask import Blueprint, request, Response, Flask, request, jsonify
import re
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
import requests
from bs4 import BeautifulSoup
from twilio.twiml.messaging_response import MessagingResponse

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return 'Hello, world'

@main.route('/webhook', methods=['POST'])
def webhook():
    #message = request.form.get('Body')
    message = request.values.get('Body', '')
    sender = request.values.get('From', '')
    response_text = "test"

    print(message)

    #Check for URL in the message
    url_match = re.search(r'http[s]?://\S+', message)
    if url_match:
        url = url_match.group(0)
        if 'facebook.com' in url:
            url = extract_actual_link(url)
        
        if url:
            text_content = extract_text_from_link(url)
            print(text_content)
            if text_content:
                summary = summarize_text(text_content)  # Assuming you have a summarization function
                bot_resp = MessagingResponse()
                response_text = bot_resp.message()
                response_text.body(summary)
                return str(bot_resp)
                #response_text = f"Summary: {summary}"
            else:
                response_text = "Could not retrieve content from the link."
    else:
        response_text = "No link"

    return Response(f"<Response><Message>{response_text}</Message></Response>", mimetype='text/xml')

def extract_text_from_link(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join(p.get_text() for p in soup.find_all('p'))
    except Exception as e:
        return None


def extract_actual_link(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            actual_link = soup.find('meta', property='og:url')['content']
            return actual_link
        return None
    except Exception as e:
        return None
    

def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, 4)

    # Combine the summarized sentences
    return ' '.join(str(sentence) for sentence in summary)