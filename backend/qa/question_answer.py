from indicnlp import common
from indicnlp.normalize.indic_normalize import DevanagariNormalizer
from indicnlp.tokenize import sentence_tokenize
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import re

class HindiQAGenerator:
    def __init__(self):
        # Initialize normalizer
        self.normalizer = DevanagariNormalizer()
        
        # Load question generation model and tokenizer
        self.qg_tokenizer = AutoTokenizer.from_pretrained("ai4bharat/MultiIndicQuestionGenerationSS")
        self.qg_model = AutoModelForSeq2SeqLM.from_pretrained("ai4bharat/MultiIndicQuestionGenerationSS")
        
        # Load Hindi QA pipeline
        self.qa_pipeline = pipeline(
            "question-answering",
            model="AVISHKAARAM/avishkaarak-ekta-hindi",
            tokenizer="AVISHKAARAM/avishkaarak-ekta-hindi"
        )

    def preprocess_text(self, text: str) -> list:
        """Normalize and split Hindi text into sentences."""
        normalized = self.normalizer.normalize(text)
        return sentence_tokenize.sentence_split(normalized, lang='hi')

    def generate_questions(self, context: str) -> list:
        """Generate a question from a Hindi sentence."""
        inputs = self.qg_tokenizer(
            f"generate question: {context}",
            return_tensors="pt",
            max_length=512,
            truncation=True
        )
        # Remove token_type_ids if present
        if 'token_type_ids' in inputs:
            inputs.pop('token_type_ids')
        outputs = self.qg_model.generate(
            **inputs,
            max_length=64,
            num_beams=5,
            early_stopping=True,
            no_repeat_ngram_size=2
        )
        question = self.qg_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return [question.strip()] if question.strip() else []

    def extract_answer(self, question: str, context: str) -> str:
        """Extract answer from context for a given question."""
        try:
            # Configure pipeline for better answer extraction
            result = self.qa_pipeline(
                question=question,
                context=context,
                max_answer_len=150,  # Increase max answer length
                handle_impossible_answer=True
            )
            
            answer = result['answer'].strip()
            score = result.get('score', 0)
            
            # Check if answer is too short (only a single character or word)
            if len(answer) <= 2 or score < 0.1:
                # If model returns short answer, use rule-based extraction
                answer = self._extract_answer_rule_based(question, context)
                
            return answer
        except Exception as e:
            # Fallback to rule-based extraction on error
            return self._extract_answer_rule_based(question, context)

    def _extract_answer_rule_based(self, question: str, context: str) -> str:
        """Extract answer using rule-based approach when model fails."""
        if re.search(r'कहाँ|कहां|स्थित|जगह', question):
            locations = re.findall(r'([^।]+में\s[^।]+(?:स्थित है|है))', context)
            if locations:
                return locations[0].strip()
                
        if re.search(r'कब|वर्ष|साल|समय', question):
            years = re.findall(r'(\d{4}(?:\s+में)?)', context)
            if years:
                # Find a sentence containing this year
                for year in years:
                    year_pattern = re.escape(year)
                    sentences = re.findall(f'[^।]*{year_pattern}[^।]*', context)
                    if sentences:
                        return sentences[0].strip()
        
        if re.search(r'किसने|कौन|किस|द्वारा', question):
            persons = re.findall(r'([^।]*(राजा|बादशाह|महाराजा|राष्ट्रपति|प्रधानमंत्री|नेता)[^।]*)', context)
            if persons:
                return persons[0][0].strip()
                
        if re.search(r'क्यों|कारण', question):
            reasons = re.findall(r'([^।]*(के लिए|के कारण|की वजह से)[^।]*)', context)
            if reasons:
                return reasons[0][0].strip()
        
        # Extract nouns from question and find related sentences
        # Extract key words from question by removing question words
        question_words = set(question.split())
        # Common Hindi question words to remove
        hindi_question_words = {'क्या', 'कौन', 'कहाँ', 'कब', 'क्यों', 'कैसे', 'किस', 'किसने', 'किसको', 'कितना', 'है', 'हैं', 'था', 'थे', 'की', 'का', 'के'}
        key_words = question_words - hindi_question_words
        
        # Find sentences that contain the most key words
        sentences = self.preprocess_text(context)
        best_match = None
        max_matches = 0
        
        for sentence in sentences:
            matches = sum(1 for word in key_words if word in sentence and len(word) > 2)
            if matches > max_matches:
                max_matches = matches
                best_match = sentence
        
        if best_match:
            return best_match
            
        # If all else fails, return the first sentence as the answer
        sentences = self.preprocess_text(context)
        if sentences:
            return sentences[0]
            
        return context  # Last resort fallback

    def generate_qa_pairs(self, hindi_text: str) -> list:
        """Run the full pipeline: preprocess, generate questions, extract answers."""
        qa_pairs = []
        sentences = self.preprocess_text(hindi_text)
        for context in sentences:
            if len(context.strip()) < 20:
                continue
            questions = self.generate_questions(context)
            for question in questions:
                answer = self.extract_answer(question, context)
                # Make sure we have a meaningful answer (not just a character or two)
                if answer and len(answer.strip()) > 3:
                    qa_pairs.append({
                        'context': context,
                        'question': question,
                        'answer': answer
                    })
        return qa_pairs

def qa_all(ocr_text):
    qa_engine = HindiQAGenerator()
    results = qa_engine.generate_qa_pairs(ocr_text)
    return results


# Example Hindi paragraph
# sample_text = """
# ताजमहल भारत के आगरा शहर में यमुना नदी के किनारे स्थित है।
#     इसका निर्माण मुगल बादशाह शाहजहाँ ने अपनी पत्नी मुमताज़ महल की याद में करवाया था।
#     ताजमहल को 1983 में यूनेस्को की विश्व धरोहर स्थल घोषित किया गया था।
#     यह संगमरमर से बना है और इसका निर्माण 1632 में शुरू हुआ था और 1653 में पूरा हुआ था।
#     इसे बनाने में लगभग बीस हज़ार कारीगरों ने काम किया था और यह मुगल वास्तुकला का सबसे सुंदर उदाहरण माना जाता है।"""
# print("🚀 Initializing Hindi QA Generator...")
# qa_engine = HindiQAGenerator()
# results = qa_engine.generate_qa_pairs(sample_text)

# print(f"\n📚 Generated {len(results)} QA Pairs:")
# for i, pair in enumerate(results, 1):
#   print(f"\n{i}. प्रश्न: {pair['question']}")
#   print(f"   उत्तर: {pair['answer']}")

# if __name__ == "__main__":
#     main()