import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from collections import Counter
from dataclasses import dataclass
from spacy.tokens import Span
from typing import List, Mapping, Dict, Tuple
import spacy
import textstat
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob
from nltk.util import ngrams
import re
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch


# Load the spaCy language model
nlp = spacy.load("en_core_web_sm")

# Load Hugging Face transformer model for coreference resolution (e.g., SpanBERT)
tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")

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
    dialogue_sentences: List[Span]

@dataclass
class AnalysisResult:
    sentence_count: int
    word_count: int
    avg_sentence_length: float
    unique_word_count: int
    lexical_density: float
    avg_word_length: float
    bigrams: Counter
    trigrams: Counter
    coherence_entities: Dict[str, int]
    sentiment_over_time: List[float]
    word_cloud: WordCloud
    syllable_count: int
    custom_theme_counts: Dict[str, int]
    coreference_resolution: Dict[str, str]
    punctuation_counts: Dict[str, int]
    emotion_counts: Dict[str, int]
    keyword_density: Dict[str, float]


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

    # Extract dialogue sentences
    dialogue_sentences = [sent for sent in sentences if re.match(r'".*"', str(sent))]

    return SegmentedText(sentences, words, pos_count_dict, entities, dialogue_sentences)


def analyze(segmented_text: SegmentedText, text: str) -> AnalysisResult:
    # Basic Analysis
    sentence_count = len(segmented_text.sentences)
    word_count = len(segmented_text.words)
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    unique_word_count = len(set(segmented_text.words))
    lexical_density = unique_word_count / word_count if word_count > 0 else 0
    avg_word_length = sum(len(word) for word in segmented_text.words) / word_count if word_count > 0 else 0

    # N-Gram Analysis
    bigrams = Counter(ngrams(segmented_text.words, 2))
    trigrams = Counter(ngrams(segmented_text.words, 3))

    # Coherence and Entity Mentions
    coherence_entities = Counter([ent.text for ent in segmented_text.entities])

    # Sentiment Analysis Over Time
    sentiment_over_time = [textstat.text_standard(str(sentence), float_output=True) for sentence in segmented_text.sentences]

    # Word Cloud Generation
    word_cloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(segmented_text.words))

    # Syllable Count
    syllable_count = sum(textstat.syllable_count(word) for word in segmented_text.words)

    # Custom Theme Analysis
    themes = ["war", "magic", "nature"]  # Example themes
    custom_theme_counts = {theme: segmented_text.words.count(theme) for theme in themes}

    # Split the text into sentences
    sentences = [str(sent) for sent in segmented_text.sentences]

    # Initialize variables for chunking
    chunks = []
    current_chunk = ""

    # Create chunks of sentences, each of which can fit within 512 tokens
    for sentence in sentences:
        current_length = len(tokenizer(current_chunk)["input_ids"])
        sentence_length = len(tokenizer(sentence)["input_ids"])

        if current_length + sentence_length <= 512:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence

    # Add the last chunk if any
    if current_chunk:
        chunks.append(current_chunk)

    # Run coreference resolution on each chunk
    coreferences = {}
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors="pt", max_length=512, truncation=True)
        with torch.no_grad():
            outputs = model(**inputs).logits
        predictions = torch.argmax(outputs, dim=-1).squeeze().tolist()
        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"].squeeze())
        clusters = {}  # Collect clusters by entity indices
        for idx, pred in enumerate(predictions):
            if pred > 0:  # Assuming non-zero indices are part of coreference clusters
                entity = tokens[idx]
                clusters.setdefault(pred, []).append(entity)
        for key, cluster_entities in clusters.items():
            main_mention = cluster_entities[0]
            for mention in cluster_entities[1:]:
                coreferences[mention] = main_mention

    # Punctuation Counts
    punctuation_counts = Counter(re.findall(r'[.,!?;:]', text))

    # Emotion Detection
    text_blob = TextBlob(" ".join(segmented_text.words))
    emotion_counts = {
        'polarity': text_blob.sentiment.polarity,
        'subjectivity': text_blob.sentiment.subjectivity
    }

    # Keyword Density
    keywords = ["power", "device", "mystery"]  # Example keywords
    keyword_density = {keyword: segmented_text.words.count(keyword) / word_count for keyword in keywords}

    return AnalysisResult(
        sentence_count, word_count, avg_sentence_length, unique_word_count, lexical_density, avg_word_length,
        bigrams, trigrams, coherence_entities, sentiment_over_time, word_cloud, syllable_count,
        custom_theme_counts, coreferences, punctuation_counts, emotion_counts, keyword_density
    )


# Example usage
if __name__ == "__main__":
    # Load example Text File
    filename = 'data/royalroad/81642.md'
    with open(filename, 'r', encoding='utf-8') as file:
        text = file.read(10_000)

    # Text Segmentation
    segmented_text = segment_text(text)
    print("Segmented Sentences:")
    for s in segmented_text.sentences[:min(3, len(segmented_text.sentences))]:
        print("-", str(s).replace("\n", "\n"))
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
                print("  -", ent.text.replace("\n", "\n"), "x", counts[ent.text])

    # Simple Analysis
    analysis_result = analyze(segmented_text, text)
    print("Sentence Count:", analysis_result.sentence_count)
    print("Word Count:", analysis_result.word_count)
    print("Average Sentence Length:", analysis_result.avg_sentence_length)
    print("Unique Word Count:", analysis_result.unique_word_count)
    print("Lexical Density:", analysis_result.lexical_density)
    print("Average Word Length:", analysis_result.avg_word_length)
    print("Syllable Count:", analysis_result.syllable_count)
    print("Punctuation Counts:", analysis_result.punctuation_counts)
    print("Emotion Counts:", analysis_result.emotion_counts)
    print("Keyword Density:", analysis_result.keyword_density)
    print("Custom Theme Counts:", analysis_result.custom_theme_counts)

    # Visualizations
    plt.figure(figsize=(10, 5))
    plt.imshow(analysis_result.word_cloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

    # Sentiment Over Time Plot
    plt.figure(figsize=(10, 5))
    plt.plot(analysis_result.sentiment_over_time)
    plt.xlabel('Sentence Index')
    plt.ylabel('Sentiment Score')
    plt.title('Sentiment Over Time')
    plt.show()
