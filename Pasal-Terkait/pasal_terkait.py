# Import modul yang dibutuhkan
import os
import pandas as pd
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Set API key OpenAI
client = OpenAI(api_key=OPENAI_API_KEY) # Ganti dengan API key Anda

# Fungsi untuk mendapatkan embedding menggunakan OpenAI
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

# Load DataFrame dari file CSV yang berisi embedding dari data undang-undang/regulasi
df_undang_undang = pd.read_csv('S:/College/Pasal Terkait/regulasi_embeddings.csv') # Ganti dengan path yang sesuai

# Load embedding dari CSV, perlu diubah menjadi tipe array agar bisa digunakan
df_undang_undang['Embedding'] = df_undang_undang['Embedding'].apply(eval)

# Teks yang sudah disummarize (misalnya hasil summarization dari berita)
teks_summarized = """
Polemik terkait akun kaskus bernama "fufufafa" menciptakan perdebatan di jagat media sosial Indonesia.
Akun ini diduga dikelola oleh Gibran Rakabuming Raka, putra sulung Presiden Joko Widodo, dan sering menghina Prabowo Subianto serta keluarganya.
Beberapa pihak, termasuk partai Gerindra, menilai ini sebagai upaya mengadu domba menjelang pelantikan presiden dan wakil presiden baru serta berpotensi merusak hubungan di antara para pemimpin.
Wakil presiden terpilih Gibran membantah memiliki akun itu dan meminta agar tidak diperpanjang pembahasannya.
Menteri Komunikasi dan Informatika, Budi Arie Setiadi, juga menyebut bahwa penyelidikan masih berjalan untuk mengidentifikasi pemilik asli akun tersebut.
Di sisi lain, muncul kekhawatiran bahwa akun palsu ini digunakan untuk memecah belah pemerintahan yang baru.
Akhir-akhir ini, banyak pihak mengklaim dan menyebarkan informasi yang tidak benar di media sosial, hingga situasi ini menciptakan kegaduhan di tengah masyarakat.
Pihak pro-Gibran dan Gerindra menekankan perlunya menjaga stabilitas dan kedamaian menjelang pelantikan, sedangkan sejumlah pengamat politik khawatir bahwa situasi ini bisa menurunkan kepercayaan publik terhadap para pemimpin baru.
"""

# Dapatkan embedding untuk teks yang disummarize
embedding_summary = get_embedding(teks_summarized, model="text-embedding-3-small")

# Hitung cosine similarity antara embedding teks summary dan setiap embedding undang-undang/regulasi
df_undang_undang['Similarity'] = df_undang_undang['Embedding'].apply(lambda x: cosine_similarity([embedding_summary], [x])[0][0])

# Tampilkan undang-undang yang paling mirip
result = df_undang_undang.sort_values(by='Similarity', ascending=False)

# Tentukan threshold similarity
threshold = 0.35

# Filter hasil berdasarkan threshold similarity
filtered_result = result[result['Similarity'] > threshold]

# Tampilkan hasil
print("Pasal terkait berdasarkan teks:")
print(filtered_result[['Bunyi_Pasal', 'Similarity']])
