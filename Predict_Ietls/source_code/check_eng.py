import spacy
import language_tool_python
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from concurrent.futures import ProcessPoolExecutor
import time
import json
import re

nltk.download('punkt') 

class CheckResult:
    pronouns_threshold = 0.5
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.language_tool = language_tool_python.LanguageTool('en-US')
        self.avoid_issue = self.load_avoid_writting()
    
    def check_writing(self, text):
        avoid_writing = []

        # Check for idioms and slangs
        idioms_and_slangs_found = [idiom for idiom in self.idioms_and_slangs if idiom in text]
        if idioms_and_slangs_found:
            avoid_writing.append(f"Idioms/Slangs found: {', '.join(idioms_and_slangs_found)}")

        # Check pronoun frequency
        pronouns = re.findall(r'\b(?:' + '|'.join(self.pronoun_list) + r')\b', text, flags=re.IGNORECASE)
        pronoun_frequency = len(pronouns) / len(word_tokenize(text))
        if pronoun_frequency > self.pronouns_threshold:
            avoid_writing.append(f"High pronoun frequency: {pronoun_frequency:.2%}")

        # Check for short forms
        short_forms_found = [short_form for short_form in self.short_forms if short_form in text]
        if short_forms_found:
            avoid_writing.append(f"Short forms found: {', '.join(short_forms_found)}")

        # Check for cliches in conclusion
        cliches_in_conclusion_found = [cliche for cliche in self.cliches_in_conclusion if cliche in text.lower()]
        if cliches_in_conclusion_found:
            avoid_writing.append(f"Cliches in conclusion found: {', '.join(cliches_in_conclusion_found)}")

        # Check for opinion phrases
        opinion_phrases_found = [opinion_phrase for opinion_phrase in self.opinion_phrases if opinion_phrase in text.lower()]
        if opinion_phrases_found:
            avoid_writing.append(f"Opinion phrases found: {', '.join(opinion_phrases_found)}")

        # Check for example phrases
        example_phrases_found = [example_phrase for example_phrase in self.example_phrases if example_phrase in text.lower()]
        if example_phrases_found:
            avoid_writing.append(f"Example phrases found: {', '.join(example_phrases_found)}")

        return avoid_writing

    def analyze_sentence_present(sentence):
        nlp = spacy.load("en_core_web_sm")

        doc = nlp(sentence)

        auxiliary_verb = None
        main_verb = None

        for token in doc:
            if token.lemma_ in ['do', 'does']:
                auxiliary_verb = token
            elif token.pos_ == 'VERB':
                main_verb = token

        if auxiliary_verb:
            if main_verb:
                if main_verb.lemma_ != main_verb.text:
                    print(f"Sentence: {sentence}")
                    print(f"Subject: {doc[0].text}")
                    print(f"Verb: {main_verb.text} -> {main_verb.lemma_} because of auxiliary verb {auxiliary_verb.lemma_}")
                    print("Wrong structure, auxiliary verbs cannot be alone")
                else:
                    print(f"Sentence: {sentence}")
                    print(f"Subject: {doc[0].text}")
                    print(f"Verb: {main_verb.text} is correct")
            else:
                print(f"Sentence: {sentence}")
                print(f"Subject: {doc[0].text}")
                print("Verb: Wrong structure, auxiliary verb cannot be alone")
        else:

            subject = doc[0]
            subject_text = subject.text.lower()

            if subject_text in ['i', 'we', 'you', 'they'] or subject.tag_ == 'NNS':
                subject_analysis = f"{subject.text} is plural subject"
                verb = doc[1]
                verb_analysis = f"{verb.text} -> {verb.lemma_} because subject is {subject.text}"
            elif subject.tag_ == 'NNP' or subject.tag_ == 'NN':
                subject_analysis = f"{subject.text} is singular noun indicating person"

                verb = doc[1]
                verb_text = verb.text.lower()
                if verb_text in ['do', 'does', 'have', 'has']:
                    if verb_text in ['do', 'does']:
                        verb_analysis = f"{verb.text} -> {verb.lemma_} because subject is {subject.text}"
                        main_verb_index = verb.i + 1
                        if main_verb_index < len(doc) and doc[main_verb_index].pos_ == 'VERB':
                            main_verb = doc[main_verb_index]
                            verb_analysis += f" {main_verb.lemma_}"
                    elif verb_text in ['have', 'has']:
                        if verb.text.lower() == 'have' and subject_text == 'she':
                            verb_analysis = f"{verb.text} -> has because subject is {subject.text}"
                        else:
                            verb_analysis = f"{verb.text} -> {verb.lemma_} because subject is {subject.text}"
                    else:
                        verb_analysis = f"{verb.text} is correct auxiliary verb"
                else:
                    if subject_text in ['he', 'she', 'it'] or subject.tag_ == 'NN':
                        if verb_text.endswith(('s', 'x', 'z', 'sh', 'ch')):
                            verb_analysis = f"{verb.text} -> {verb.lemma_ + 'es'} because subject is {subject.text}"
                        else:
                            verb_analysis = f"{verb.text} -> {verb.lemma_ + 's'} because subject is {subject.text}"
                    else:
                        verb_analysis = f"{verb.text} is correct main verb"
            else:
                subject_analysis = f"{subject.text} is singular subject in (he, she, it)"
                verb = doc[1]
                verb_text = verb.text.lower()
                if verb_text in ['do', 'does', 'have', 'has']:
                    if verb_text in ['do', 'does']:
                        verb_analysis = f"{verb.text} -> {verb.lemma_} because subject is {subject.text}"
                        main_verb_index = verb.i + 1
                        if main_verb_index < len(doc) and doc[main_verb_index].pos_ == 'VERB':
                            main_verb = doc[main_verb_index]
                            verb_analysis += f" {main_verb.lemma_}"
                    elif verb_text in ['have', 'has']:
                        if verb.text.lower() == 'have' and subject_text == 'she':
                            verb_analysis = f"{verb.text} -> has because subject is {subject.text}"
                        else:
                            verb_analysis = f"{verb.text} -> {verb.lemma_} because subject is {subject.text}"
                    else:
                        verb_analysis = f"{verb.text} is correct auxiliary verb"
                else:
                    if subject_text in ['he', 'she', 'it'] or subject.tag_ == 'NN':
                        if verb_text.endswith(('s', 'x', 'z', 'sh', 'ch')):
                            verb_analysis = f"{verb.text} -> {verb.lemma_ + 'es'} because subject is {subject.text}"
                        else:
                            verb_analysis = f"{verb.text} -> {verb.lemma_ + 's'} because subject is {subject.text}"
                    else:
                        verb_analysis = f"{verb.text} is correct main verb"

            print(f"Subject: {subject_analysis}")
            print(f"Verb: {verb_analysis}")

            if subject.text.lower() == 'i' or subject.tag_ == 'NNS':
                print("Sentence is correct")
            elif subject.tag_ == 'NNP' or subject.tag_ == 'NN':
                if subject_text in ['he', 'she', 'it']:
                    if verb_text in ['does', 'has']:
                        print("Sentence is correct")
            elif subject.text.lower() in ['he', 'she', 'it']:
                if verb_text in ['does', 'has']:
                    print("Sentence is correct")

# checker = CheckResult()
# text = "he are not bad, she are gonna go to the theter this last week and how older you are. I has no iead why you are here last nights. can you gimme the results ASAP. In conclusion, I believe that using cliches such as 'in conclusion' is not advisable. You should avoid them."
# words = word_tokenize(text)
# print("Tokenized Words:", words)
# start_time = time.time()

# # Wrap the single text in a list to create a document
# documents = [text]

# vectorizer = TfidfVectorizer()

# # Pass the list of documents to fit_transform
# X = vectorizer.fit_transform(documents)

# print("Feature Names:", vectorizer.get_feature_names_out())
# print("TF-IDF Matrix:\n", X.toarray())


# print("Feature Names:", vectorizer.get_feature_names_out())  # Corrected line
# print("TF-IDF Matrix:\n", X.toarray())

# fast_check = checker.check_writing(text)

# errors, cumulative_corrections = checker.check_grammar(text)

# # Accumulate corrections for final output
# final_corrected_text = text

# if errors:
#     for error in errors:
#         print(f"Error Type: {error['error_type'] if 'error_type' in error else 'N/A'}")
#         print(f"Error Message: {error['error_message'] if 'error_message' in error else 'N/A'}")
#         print(f"Corrections: {error['corrections'] if 'corrections' in error else 'N/A'}")
#         print(f"Tokenized Sentences: {error['tokenized_sentences'] if 'tokenized_sentences' in error else 'N/A'}")
#         print(f"POS Tags: {error['pos_tags'] if 'pos_tags' in error else 'N/A'}")
#         print(f"Named Entities: {error['named_entities'] if 'named_entities' in error else 'N/A'}")

#         # Update the final corrected text with the corrected text
#         final_corrected_text = error['corrected_text'] if 'corrected_text' in error else final_corrected_text

# else:
#     print("No errors found.")

# print(f"First Text: {text}")
# # Display the final corrected text
# print(f"Final Corrected Text: {final_corrected_text}")
# end_time = time.time()
# print(f"Processing time: {end_time - start_time} seconds")
