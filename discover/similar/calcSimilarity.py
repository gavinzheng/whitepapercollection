
import nltk
from nltk.corpus import brown
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from gensim import corpora, models, similarities
import logging

courses = [line.strip() for line in file('coursera_corpus')]
courses_name = [course.split('\t')[0] for course in courses]
print courses_name[0:10]

texts_lower = [[word for word in document.lower().split()] for document in courses]
print texts_lower[0]

texts_tokenized = [[word.lower() for word in word_tokenize(document.decode('utf-8'))] for document in courses]
print texts_tokenized[0]


english_stopwords = stopwords.words('english')
print english_stopwords

texts_filtered_stopwords = [[word for word in document if not word in english_stopwords] for document in texts_tokenized]
print texts_filtered_stopwords[0]

english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
texts_filtered = [[word for word in document if not word in english_punctuations] for document in texts_filtered_stopwords]
print texts_filtered[0]

st = LancasterStemmer()
texts_stemmed = [[st.stem(word) for word in docment] for docment in texts_filtered]
print texts_stemmed[0]

all_stems = sum(texts_stemmed, [])
stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
index = similarities.MatrixSimilarity(lsi[corpus])
print courses_name[210]

ml_course = texts[210]
ml_bow = dictionary.doc2bow(ml_course)
ml_lsi = lsi[ml_bow]
print ml_lsi
sims = index[ml_lsi]
sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])

print sort_sims[0:10]






