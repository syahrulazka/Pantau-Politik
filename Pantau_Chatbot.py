import os
import hashlib
import logging
import traceback
import pandas as pd
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document, SystemMessage, HumanMessage, AIMessage
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize API Key for OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.5)

# Configure logging
logging.basicConfig(filename='data_loading.log', level=logging.WARNING)

# Cache for processed files
processed_files = set()

def file_hash(filepath):
    """Create a hash for a file to check if it has been processed."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()

def is_file_processed(filepath):
    """Check if a file has already been processed."""
    hash_value = file_hash(filepath)
    if hash_value in processed_files:
        return True
    processed_files.add(hash_value)
    return False

def load_pdf_to_vectorstore(pdf_path):
    """Load PDF and split into smaller documents."""
    try:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = splitter.split_documents(documents)
        
        # Add metadata (source)
        for doc in documents:
            doc.metadata = {"source": pdf_path}
        
        return documents
    except Exception as e:
        logging.warning(f"Error loading PDF: {e}")
        traceback.print_exc()
        return []

def validate_csv_data(df):
    """Validate and clean CSV data."""
    df = df.dropna(subset=['Title', 'Content'])
    df = df[df['Content'].str.len() > 50]
    return df

def remove_duplicates(df):
    """Remove duplicates from the DataFrame."""
    return df.drop_duplicates(subset=['Title', 'Content'])

def load_csv_to_vectorstore(csv_path):
    """Load data from CSV and prepare for vector store."""
    try:
        df = pd.read_csv(csv_path)
        df = validate_csv_data(df)
        df = remove_duplicates(df)

        documents = [
            Document(page_content=f"{row['Title']}\n\n{row['Content']}", metadata={"source": csv_path})
            for _, row in df.iterrows()
        ]

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = splitter.split_documents(documents)
        
        return documents
    except Exception as e:
        logging.warning(f"Error loading CSV: {e}")
        traceback.print_exc()
        return []

def create_vector_store(documents):
    """Create a vector store from documents using embeddings."""
    embedding_function = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-small")
    vectorstore = Chroma(
        collection_name="my_collection",
        embedding_function=embedding_function,
        persist_directory="chroma_vectorstore"
    )
    
    vectorstore.add_documents(documents)
    vectorstore.persist()
    return vectorstore

def load_or_create_vectorstore(pdf_path, csv_path):
    """Load or create the vector store."""
    embedding_function = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-small")
    
    # Check if a vector store already exists and load it if available
    if os.path.exists("chroma_vectorstore"):
        print("Memuat vectorstore yang sudah ada...")
        vectorstore = Chroma(
            collection_name="my_collection",
            embedding_function=embedding_function,
            persist_directory="chroma_vectorstore"
        )
        return vectorstore
    else:
        print("Membuat vectorstore baru...")
        pdf_docs = load_pdf_to_vectorstore(pdf_path)
        csv_docs = load_csv_to_vectorstore(csv_path)
        combined_docs = pdf_docs + csv_docs
        
        if not combined_docs:
            raise ValueError("No documents were loaded successfully.")
        
        return create_vector_store(combined_docs)

# List to store conversation history
messages = [SystemMessage(content="Anda adalah asisten politik yang memberikan jawaban dalam bahasa Indonesia.")]

def get_gpt4_answer(human_message):
    """Get an answer from the GPT-4 model."""
    messages.append(HumanMessage(content=human_message))
    response = llm.invoke(messages)
    messages.append(AIMessage(content=response.content))
    return response.content

def search_and_answer(human_message, vectorstore):
    """Search for relevant documents and generate an answer using the LLM."""
    try:
        search_results = vectorstore.similarity_search(human_message, k=3)
        if not search_results:
            return "Maaf, saya tidak memiliki informasi tentang pertanyaan tersebut."
        
        # Menggunakan set untuk menyimpan sumber unik
        unique_sources = set()
        context = ""
        
        for doc in search_results:
            source = doc.metadata.get('source', 'Tidak diketahui')
            if source not in unique_sources:
                unique_sources.add(source)
                context += f"Sumber: {source} - {doc.page_content}\n"

        if not context:
            return "Maaf, saya tidak menemukan informasi yang relevan."

        messages.append(SystemMessage(content=f"Context: {context}"))
        
        # Generate the answer
        answer = get_gpt4_answer(human_message)
        return f"Pertanyaan: {human_message}\n\nJawaban: {answer}\n\nInformasi ini berasal dari:\n{context}"
    except Exception as e:
        logging.warning(f"Error in search_and_answer: {e}")
        traceback.print_exc()
        return "Terjadi kesalahan dalam pencarian."

# Main loop program
if __name__ == "__main__":
    pdf_path = r"D:\File Jurnal LLM\4208-12183-3-PB.pdf"
    csv_path = r"D:\File Jurnal LLM\fufufafa_clean_no_url.csv"

    try:
        # Load or create vectorstore
        vectorstore = load_or_create_vectorstore(pdf_path, csv_path)
    except Exception as e:
        print(f"Gagal membuat atau memuat vectorstore: {e}")
        exit(1)

    print("Masuk ke dalam loop...")
    while True:
        try:
            pertanyaan = input("Kamu: ")
            if pertanyaan.lower() == "exit":
                print("Chatbot: Terima kasih, sampai jumpa!")
                break
            elif pertanyaan.lower() == "lihat riwayat":
                for msg in messages:
                    if isinstance(msg, HumanMessage):
                        print(f"Kamu: {msg.content}")
                    elif isinstance(msg, AIMessage):
                        print(f"Chatbot: {msg.content}")
                continue

            jawaban = search_and_answer(pertanyaan, vectorstore)
            print(f"Chatbot: {jawaban}")
        except KeyboardInterrupt:
            print("\nProgram dihentikan oleh pengguna.")
            break
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            traceback.print_exc()
    
