# Goal 1: Text Segmentation and Parsing
# This script will take a text input, break it down into sentences and words, and calculate basic metrics like sentence count, word count, and average sentence length.

import spacy
import textstat
from collections import Counter

# Load the spaCy language model
nlp = spacy.load("en_core_web_sm")

def segment_text(text):
    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences and words
    sentences = list(doc.sents)
    words = [token.text for token in doc if token.is_alpha]

    # Calculate metrics
    sentence_count = len(sentences)
    word_count = len(words)
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    unique_words = set(words)
    unique_word_count = len(unique_words)
    lexical_density = unique_word_count / word_count if word_count > 0 else 0
    avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0

    # Part-of-Speech (POS) Tag Count
    pos_counts = doc.count_by(spacy.attrs.POS)
    pos_count_dict = {doc.vocab[pos].text: count for pos, count in pos_counts.items()}

    # Readability Score
    readability_score = textstat.flesch_reading_ease(text)

    # Named Entity Recognition (NER)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    entity_count = Counter([ent.label_ for ent in doc.ents])

    # Sentiment Analysis (basic using textstat's sentiment)
    sentiment_score = textstat.text_standard(text, float_output=True)

    # Print the results
    print("Sentence Count:", sentence_count)
    print("Word Count:", word_count)
    print("Average Sentence Length:", avg_sentence_length)
    print("Unique Word Count:", unique_word_count)
    print("Lexical Density:", lexical_density)
    print("Average Word Length:", avg_word_length)
    print("POS Tag Count:", pos_count_dict)
    print("Readability Score (Flesch Reading Ease):", readability_score)
    print("Named Entities:", entities)
    print("Entity Count:", entity_count)
    print("Sentiment Score (Text Standard):", sentiment_score)

    # Return segmented sentences and words
    return sentences, words

# Example usage
if __name__ == "__main__":
    filename = 'data/gutenberg/68283.txt'  # Cthulhu's Tales

    with open(filename, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    sentences, words = segment_text(file_contents)

    # # Print segmented sentences and words
    # print("\nSegmented Sentences:")
    # for i, sentence in enumerate(sentences, 1):
    #     print(f"{i}: {sentence}")
    #
    # print("\nSegmented Words:")
    # print(words)
