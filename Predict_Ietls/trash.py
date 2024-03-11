import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_sentence(sentence):

    doc = nlp(sentence)

    auxiliary_verb = None
    main_verb = None

    for token in doc:
        if token.lemma_ in ['do', 'does', 'did']:
            auxiliary_verb = token
        elif token.pos_ == 'VERB':
            main_verb = token

    if auxiliary_verb:
        if main_verb:
            if main_verb.lemma_ == main_verb.text:
                return {
                    "sentence": sentence,
                    "subject": doc[0].text,
                    "verb": f"{main_verb.text} -> {main_verb.lemma_} because of auxiliary verb {auxiliary_verb.lemma_}",
                    "error": "Wrong structure, auxiliary verbs cannot be alone",
                    "tense": None
                }
            else:
                # Check if the main verb is in past tense
                if main_verb.tag_ == 'VBD':
                    tense = "past"
                else:
                    tense = "present"
                    
                print(f"\nSentence: {sentence}")
                print(f"Subject: {doc[0].text}")
                print(f"Verb: {main_verb.text} is correct")
                print(f"Tense: {tense}")

                return {
                    "sentence": sentence,
                    "subject": doc[0].text,
                    "verb": f"{main_verb.text} is correct",
                    "error": None,
                    "tense": tense
                }
                
        else:
            print(f"Sentence: {sentence}")
            print(f"Subject: {doc[0].text}")
            print("Verb: Wrong structure, auxiliary verb cannot be alone")
            
            return {
                "sentence": sentence,
                "subject": doc[0].text,
                "verb": "No main verb found",
                "error": None,
                "tense": None
            }
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
        print(f"\nSentence: {sentence}")
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

sentence1 = "I do loved running slow"
sentence2 = "She like to go outside"
sentence3 = "He does like watching TV shows"
sentence4 = "He are watching TV shows"

result1 = analyze_sentence(sentence1)
result2 = analyze_sentence(sentence2)
result3 = analyze_sentence(sentence3)
result4 = analyze_sentence(sentence4)

text_to_analyze = "I have a car. He are watching TV shows. They is playing football."
# analyze_sentence(text_to_analyze)
sentences = [sent.text for sent in nlp(text_to_analyze).sents]
for sentence in sentences:
    analyze_sentence(sentence)