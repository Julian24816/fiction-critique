# Goal 1: Text Segmentation and Parsing
# This script will take a text input, break it down into sentences and words, and calculate basic metrics like sentence count, word count, and average sentence length.
from typing import List, Mapping

import spacy
import textstat
from collections import Counter
from dataclasses import dataclass

from spacy.tokens import Span

# Load the spaCy language model
nlp = spacy.load("en_core_web_sm")

@dataclass
class Entity:
    text: str
    label: str

@dataclass
class SegmentedText:
    sentences: List[Span]
    words: List[str]
    pos_count_dict: Mapping[str, int]
    entities: List[Entity]


@dataclass
class AnalysisResult:
    sentence_count: int
    word_count: int
    avg_sentence_length: float
    unique_word_count: int
    lexical_density: float
    avg_word_length: float

def segment_text(text: str) -> SegmentedText:
    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences and words
    sentences = list(doc.sents)
    words = [token.text for token in doc if token.is_alpha]

    # Part-of-Speech (POS) Tag Count
    pos_count_dict = {doc.vocab[pos].text: count for pos, count in doc.count_by(spacy.attrs.POS).items()}

    # Named Entity Recognition (NER)
    entities = [Entity(ent.text, ent.label_) for ent in doc.ents]

    return SegmentedText(sentences, words, pos_count_dict, entities)


def analyze(segmented_text: SegmentedText) -> AnalysisResult:
    sentence_count = len(segmented_text.sentences)
    word_count = len(segmented_text.words)
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    unique_word_count = len(set(segmented_text.words))
    lexical_density = unique_word_count / word_count if word_count > 0 else 0
    avg_word_length = sum(len(word) for word in segmented_text.words) / word_count if word_count > 0 else 0
    return AnalysisResult(sentence_count, word_count, avg_sentence_length, unique_word_count, lexical_density, avg_word_length)


# Example usage
if __name__ == "__main__":
    # Load example Text File
    filename = 'data/The Call of Cthulhu.md'
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read()

    # Text Segmentation
    segmented_text = segment_text(text)
    print("Segmented Sentences:")
    for s in segmented_text.sentences[:min(3, len(segmented_text.sentences))]:
        print("-", str(s).replace("\n", "\\n"))
    if len(segmented_text.sentences) > 3: print("- ...")
    print("Segmented Words (Unique):", ", ".join(list(set(segmented_text.words))[:50]), "...")
    print("POS Tag Count:")
    for pos, count in segmented_text.pos_count_dict.items():
        print("-", pos, count)
    print("Named Entities:")
    types = Counter([ent.label for ent in segmented_text.entities])
    counts = Counter([ent.text for ent in segmented_text.entities])
    for ent_type in types:
        print("-", ent_type)
        for ent in segmented_text.entities:
            if ent.label == ent_type:
                print("  -", ent.text.replace("\n", "\\n"), "x", counts[ent.text])

    # Simple Analysis
    analysis_result = analyze(segmented_text)
    print("Sentence Count:", analysis_result.sentence_count)
    print("Word Count:", analysis_result.word_count)
    print("Average Sentence Length:", analysis_result.avg_sentence_length)
    print("Unique Word Count:", analysis_result.unique_word_count)
    print("Lexical Density:", analysis_result.lexical_density)
    print("Average Word Length:", analysis_result.avg_word_length)

    # Readability Score
    readability_score = textstat.flesch_reading_ease(text)
    print("Readability Score (Flesch Reading Ease):", readability_score)

    # Sentiment Analysis (basic using textstat's sentiment)
    sentiment_score = textstat.text_standard(text, float_output=True)
    print("Sentiment Score (Text Standard):", sentiment_score)
