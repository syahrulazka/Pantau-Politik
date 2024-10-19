import openai
import time
import os
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
from readData import read_news_content

load_dotenv()  
openai.api_key = os.getenv('OPENAI_API_KEY')

# Rate limiting: 3 calls per minute
CALLS = 3
RATE_LIMIT = 60

@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
def call_gpt_api(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes long news text focused in indonesian politics."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content'].strip()
    except openai.error.RateLimitError:
        print("Rate limit exceeded. Waiting before retrying...")
        time.sleep(60)
        return call_gpt_api(prompt)

def summarize_text(text):
    prompt = f"""Summarize the following collection of long news articles into a short narrative that can be read and understood in less than two minutes. Use point of view as an informative news medium. Use clear and simple language so that readers from different backgrounds can easily understand the political issue being discussed. Separate the information into 3 short paragraphs (3 sections) so that readers can easily understand the flow. It is as if you are a journalist writing a news story.\n\n{text}\n\nSummary:"""
    return call_gpt_api(prompt)

def main():
    csv_file_path = '.\data\scraped_fufufafa_clean.csv'
    text_news = read_news_content(csv_file_path)

    summary = summarize_text(text_news)
    # print("Summary:")
    print(summary)
    return summary

if __name__ == "__main__":
    main()