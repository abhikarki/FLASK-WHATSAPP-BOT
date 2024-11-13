from flask import Blueprint, request, Response
import re
import requests
from bs4 import BeautifulSoup

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

main = Blueprint('main', __name__)

@main.route('/webhook', methods=['POST'])
def webhook():
    message = request.form.get('Body')
    sender = request.form.get('From')

    #Check for URL in the message
    url_match = re.search(r'http[s]?://\S+', message)
    if url_match:
        url = url_match.group(0)
        text_content = extract_text_from_link(url)
        if text_content:
            summary = summarize_text(text_content)  # Assuming you have a summarization function
            response_text = f"Summary: {summary}"
        else:
            response_text = "Could not retrieve content from the link."
    else:
        response_text = "No link found in the message."

    return Response(f"<Response><Message>{response_text}</Message></Response>", mimetype='text/xml')

def extract_text_from_link(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join(p.get_text() for p in soup.find_all('p'))
    except Exception as e:
        return None

def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary = summarizer(parser.document, 4)

    # Combine the summarized sentences
    return ' '.join(str(sentence) for sentence in summary)