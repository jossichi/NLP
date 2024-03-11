import spacy
import nltk
from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from spellchecker import SpellChecker
from nltk.tokenize import word_tokenize
from nltk import pos_tag as nltk_pos_tag

# Load spaCy's English language model
nlp = spacy.load("en_core_web_sm")
nltk.download('words', download_dir='D:\\PROJECT\\Predict_Ietls\\data', quiet=True)

def structure_sentences(sentence):
    # Analyze the sentence with spaCy
    doc = nlp(sentence)

    # Print information about the components in the sentence
    print("\nSentence:", sentence)
    print("Subject:", [token.text for token in doc if token.dep_ == 'nsubj'])
    print("Object:", [token.text for token in doc if token.dep_ == 'dobj'])
    print("Verb:", [token.text for token in doc if token.pos_ == 'VERB'])
    print("Adverbial:", [token.text for token in doc if token.pos_ == 'ADV'])
    complements = [token.text for token in doc if token.dep_ == 'attr' or token.dep_ == 'prep']
    print("Complement:", complements)

def analyze_complements(sentence):
    # Analyze the sentence with spaCy
    doc = nlp(sentence)

    # Find subjects, objects, and verbs in the sentence
    subjects = [token for token in doc if token.dep_ == 'nsubj']
    objects = [token for token in doc if token.dep_ == 'dobj']
    verbs = [token for token in doc if token.pos_ == 'VERB']

    # Analyze complements for each main component in the sentence
    for verb in verbs:
        verb_complements = [token.text for token in doc if token.head == verb and token.dep_ in ['attr', 'prep', 'advcl']]
        if verb_complements:
            print(f'"{verb.text}": Complements for verb "{verb.text}": {verb_complements}')

    for subject in subjects:
        subject_complements = [token.text for token in doc if token.head == subject and token.dep_ in ['attr', 'prep', 'advcl']]
        if subject_complements:
            print(f'"{subject.text}": Complements for subject "{subject.text}": {subject_complements}')

    for obj in objects:
        obj_complements = [token.text for token in doc if token.head == obj and token.dep_ in ['attr', 'prep', 'advcl']]
        if obj_complements:
            print(f'"{obj.text}": Complements for object "{obj.text}": {obj_complements}')

nltk.download('averaged_perceptron_tagger')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

def analyze_tenses(sentence):
    # Analyze the sentence with spaCy
    doc = nlp(sentence)

    # Find verbs and determine their tenses
    verbs_tenses = {token.text: token.morph.get("Tense") for token in doc if token.pos_ == "VERB"}

    # Print the sentence and tenses of each verb
    print("\nSentence:", sentence)
    print("Tenses of each verb:")
    for verb, tense in verbs_tenses.items():
        print(f"{verb}: {tense}")

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def detect_short_forms_and_phrasal_verbs(text, abbreviation_dict):
    # Phân tích câu với spaCy
    doc = nlp(text)

    # Duyệt qua các token trong câu và kiểm tra xem có phải từ viết tắt hoặc phrasal verb không
    for token in doc:
        
        phrase = ' '.join(t.text for t in token.subtree)
        
        if phrase.isupper() and len(phrase) > 1:
            full_form = abbreviation_dict.get(phrase, phrase)
            print(f"short forms: {phrase} (Full form: {full_form})")
            
        if token.text.isupper() and len(token.text) > 1:
            full_form = abbreviation_dict.get(token.text, token.text)
            print(f"Short form: {token.text} (Full form: {full_form})")
        if token.pos_ == 'VERB' and 'prt' in [child.dep_ for child in token.children]:
            print(f"Phrasal Verb: {token.text} {token.children}")

def check_spelling(text, abbreviation_dict):
    # Tách văn bản thành từng từ
    words_list = word_tokenize(text)

    # Lấy các phần loại từ (part-of-speech tags)
    pos_tags = nltk_pos_tag(words_list)

    # Tạo một đối tượng SpellChecker
    spell = SpellChecker()

    # Tải từ điển Cambridge hoặc sử dụng từ điển có sẵn trong NLTK (English words)
    cambridge_dict = set(nltk.corpus.words.words())

    # Kiểm tra từng từ với từ điển và đếm lỗi
    errors = []
    for word, pos_tag in zip(words_list, pos_tags):
        # Nếu từ là danh từ riêng hoặc là từ viết tắt trong abbreviation_dict, không sửa lỗi chính tả
        if pos_tag[1] == 'NNP' or word in abbreviation_dict:
            continue

        corrected_word = spell.correction(word)
        if corrected_word != word:
            # Nếu từ được sửa không xuất hiện trong từ điển Cambridge, thì thực hiện tìm kiếm gợi ý
            suggestions = spell.unknown([word])
            most_different_suggestion = min(suggestions, key=lambda x: nltk.edit_distance(word, x))
            errors.append((word, corrected_word, most_different_suggestion))
            if word not in cambridge_dict:
                # Nếu từ không xuất hiện trong từ điển Cambridge, thì thực hiện tìm kiếm gợi ý
                suggestions = [s for s in cambridge_dict if nltk.edit_distance(word, s) <= 2]
                if suggestions:
                    most_similar_suggestion = min(suggestions, key=lambda x: nltk.edit_distance(word, x))
                    errors.append((word, corrected_word, most_similar_suggestion))

    if not errors:
        return "Great writing - No spelling errors found"
    else:
        print("Spelling errors:")
        for original, corrected, suggestion  in errors:
            print(f"Error found: '{original}' should be '{corrected}') ")
        return "Spelling errors found"

def analyze_sentence_present(sentence):
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
            if main_verb.lemma_ == main_verb.text:
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
   
text = "At 35 years old she is starting over again, alone in a foreign country, without so much as a photograph or letter from her old life – just a sparse room with bare white walls. But it’s home, and the first place she’s had to herself after a life lived in the shadows. Chae-ran is among a number of women who fled North Korea – only to be trafficked and sexually exploited in China, where a gender imbalance has created a black market for brides. She managed to stage a second escape nearly two decades later, through Laos and Thailand. But opportunities for others to take the same path have narrowed since the pandemic, experts say – leaving untold numbers of North Korean girls and women trapped in servitude. CNN is identifying Chae-ran by a pseudonym for the safety of her family back in North Korea – and the son she left behind in China. OMG, I can't believe he stood me up. That's a real pain in the neck, etc"
abbreviation_dict = {'OMG': 'Oh my God', 'etc': 'et cetera', 'CNN':'Cable News Network'}

print("Analyze Structured Sentences:\n")
structure_sentences(text)
print("Analyze Complements in Sentences:\n")
analyze_complements(text)
print("Analyze Tenses in Sentences:\n")
sentences = [sent.text for sent in nlp(text).sents]

for sentence in sentences:
    analyze_tenses(sentence)
    print("\nAnalyze short forms and phrasal verbs\n")
    detect_short_forms_and_phrasal_verbs(sentence, abbreviation_dict)
    analyze_sentence_present(sentence)

print("Find incorrect spelling")
corrected_text = check_spelling(text, abbreviation_dict)
print(f"\nOriginal: {text}\n")
print(f"Result corrections: {corrected_text}")