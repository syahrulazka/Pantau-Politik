import os
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import re

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

# Fungsi untuk membersihkan teks setelah ekstraksi dari PDF
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Fungsi untuk mengekstrak teks dari file PDF menggunakan PyPDF2
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

# Fungsi untuk membaca semua file PDF dalam folder dan mengekstrak teksnya
def extract_texts_from_folder(folder_path):
    texts = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            cleaned_text = clean_text(text)  # Bersihkan teks
            texts.append((filename, cleaned_text))  # Simpan nama file dan teks yang sudah dibersihkan
    return texts

# Lokasi folder berisi file PDF undang-undang
folder_path = 'S:\College\Pasal Terkait\database_regulasi' # Ganti dengan path yang sesuai

# Ekstrak teks dari semua file PDF di dalam folder
pdf_texts = extract_texts_from_folder(folder_path)

# Simpan semua undang-undang dalam DataFrame
data_undang_undang = {'File': [], 'Bunyi_Pasal': [], 'Embedding': []}
for filename, text in pdf_texts:
    undang_undang_list = text.split('Pasal')[1:]  # Hilangkan bagian sebelum pasal pertama
    undang_undang_list = ['Pasal ' + u.strip() for u in undang_undang_list]

    for pasal in undang_undang_list:
        embedding = get_embedding(pasal, model="text-embedding-3-small")  # Dapatkan embedding untuk setiap pasal
        data_undang_undang['File'].append(filename)
        data_undang_undang['Bunyi_Pasal'].append(pasal)
        data_undang_undang['Embedding'].append(embedding)

# Konversi ke DataFrame
df_undang_undang = pd.DataFrame(data_undang_undang)

# Simpan DataFrame ke file CSV agar tidak perlu menghitung ulang embedding
df_undang_undang.to_csv('regulasi_embeddings.csv', index=False)
