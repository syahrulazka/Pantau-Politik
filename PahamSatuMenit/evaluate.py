from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
from nltk.tokenize import word_tokenize
from bert_score import score
from readData import read_news_content
import nltk
nltk.download('wordnet')
nltk.download('punkt_tab')
nltk.download('punkt')

# Run evaluation and display results
# Make sure generated_summary and reference_summary are strings
generated_summary = '''Akun media sosial Kaskus bernama "fufufafa" menjadi sorotan dalam konteks politik Indonesia setelah diduga terhubung dengan Gibran Rakabuming Raka, wakil presiden terpilih sekaligus putra Presiden Joko Widodo (Jokowi). Akun ini dikatakan sering memposting komentar negatif terhadap Prabowo Subianto dan keluarganya, sehingga menimbulkan spekulasi mengenai kepemilikannya dan niat di balik unggahannya. Meski Gibran membantah memiliki akun tersebut, banyak warga net yang melakukan investigasi untuk mencari bukti keterkaitannya.

Isu ini tidak hanya direspons oleh Gibran, tetapi juga oleh partai politik yang terlibat, seperti Gerindra. Ketua Harian Gerindra, Sufmi Dasco Ahmad, menilai isu ini merupakan upaya untuk memecah belah hubungan antara Jokowi dan Prabowo. Dia menekankan pentingnya persatuan di tengah situasi transisi pemerintahan yang bisa membuat masyarakat cemas jika terganggu. Selain itu, pihak Gerindra dan Projo (Relawan Jokowi) melaporkan akun dan situs palsu yang mencatut nama partai mereka untuk upaya adu domba.

Menteri Komunikasi dan Informatika, Budi Arie Setiadi, mengatakan bahwa pihaknya sedang menyelidiki kepemilikan akun fufufafa. Dia menambahkan bahwa siapa pun yang merasa dirugikan oleh unggahan tersebut seharusnya melapor kepada pihak berwenang. Kontroversi ini menunjukkan betapa rumitnya dinamika politik menjelang pelantikan dan bisa menimbulkan krisis kepercayaan di kalangan pemilih dan masyarakat umum.'''  # Assuming main() returns the generated summary

reference_summary = str(read_news_content('.\data\scraped_fufufafa_clean.csv'))  # Assuming read_news_content() returns the reference summary

# Function to calculate ROUGE score with manual tokenization
def calculate_rouge(generated, reference):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    # Tokenize text manually
    generated_tokens = ' '.join(nltk.word_tokenize(generated))
    reference_tokens = ' '.join(nltk.word_tokenize(reference))
    
    # Score using tokenized text
    scores = scorer.score(reference_tokens, generated_tokens)
    return scores

def calculate_bleu(generated, reference):
    reference_tokens = [nltk.word_tokenize(reference)]  # Tokenize reference
    generated_tokens = nltk.word_tokenize(generated)  # Tokenize generated summary
    score = sentence_bleu(reference_tokens, generated_tokens)
    return score

def calculate_meteor(generated, reference):
    # Tokenize the generated summary and reference
    generated_tokens = word_tokenize(generated)
    reference_tokens = word_tokenize(reference)
    
    # Calculate METEOR score
    score = meteor_score([reference_tokens], generated_tokens)
    return score

def calculate_bert_score(generated, reference):
    P, R, F1 = score([generated], [reference], lang="en", verbose=False)
    return {"precision": P.item(), "recall": R.item(), "f1": F1.item()}

def display_all_metrics(generated, reference):
    rouge_scores = calculate_rouge(generated, reference)
    print("ROUGE Scores:")
    print(f"  ROUGE-1  -> Precision: {rouge_scores['rouge1'].precision:.2f}, Recall: {rouge_scores['rouge1'].recall:.2f}, F1-Score: {rouge_scores['rouge1'].fmeasure:.2f}")
    print(f"  ROUGE-2  -> Precision: {rouge_scores['rouge2'].precision:.2f}, Recall: {rouge_scores['rouge2'].recall:.2f}, F1-Score: {rouge_scores['rouge2'].fmeasure:.2f}")
    print(f"  ROUGE-L  -> Precision: {rouge_scores['rougeL'].precision:.2f}, Recall: {rouge_scores['rougeL'].recall:.2f}, F1-Score: {rouge_scores['rougeL'].fmeasure:.2f}")
    
    # Calculate BLEU score
    bleu_score = calculate_bleu(generated, reference)
    print(f"\nBLEU Score: {bleu_score:.2f}")
    
    # Calculate METEOR score
    meteor = calculate_meteor(generated, reference)
    print(f"\nMETEOR Score: {meteor:.2f}")
    
    # Calculate BERTScore
    bert_scores = calculate_bert_score(generated, reference)
    print(f"\nBERTScore:")
    print(f"  Precision: {bert_scores['precision']:.2f}, Recall: {bert_scores['recall']:.2f}, F1-Score: {bert_scores['f1']:.2f}")

display_all_metrics(generated_summary, reference_summary)