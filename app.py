from flask import Flask, request, jsonify, render_template, make_response
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import re
from googletrans import Translator, LANGUAGES
from summarizer import summarize_text

app = Flask(__name__)

@app.after_request
def add_cache_control(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def extract_video_id(url):
    """Extracts video ID from various YouTube URL formats."""
    print(f"Extracting video ID from URL: {url}")  # Debugging statement
    match = re.search(r"(?:youtu\.be\/|youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=))([\w-]{11})", url)
    if match:
        video_id = match.group(1)
        print(f"Extracted Video ID: {video_id}")  # Debugging statement
        return video_id
    else:
        print("Failed to extract video ID.")  # Debugging statement
    return None

def get_translation(text, selected_language):
    """Handles the synchronous translation by splitting large texts into smaller chunks."""
    translator = Translator()
    print(f"Selected Language in get translation function: {selected_language}")  # Debugging statement
    try:
        print(f"Translating text to {selected_language}...")  # Debugging statement
        chunk_size = 500  # Adjust if needed
        translated_chunks = []

        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size]
            translated_chunk = translator.translate(chunk, src="en", dest=selected_language).text
            translated_chunks.append(translated_chunk)

        full_translation = " ".join(translated_chunks)
        print(f"Translation Result is ready")  # Debugging statement
        return full_translation

    except Exception as e:
        print(f"Error during translation: {str(e)}")  # Debugging statement
        return None

def clean_transcript_text(text):
    clean_transcript_text = text.replace('"', '').replace("'", '') 
    clean_transcript_text = str(clean_transcript_text)
    return clean_transcript_text

@app.route("/", methods=["GET", "POST"])
def index():
    transcript_text = None
    error_message = None
    selected_language = "en"
    translated_text = None
    summary = None  # Assign a default value
    
    if request.method == "POST":
        video_url = request.form.get("video_url")
        print(f"Video URL: {video_url}")  # Debugging statement
        
        if not video_url:
            error_message = "Video URL is required!"
            print(error_message)  # Debugging statement
        else:
            selected_language = request.form.get("language", "en")
            print(f"Selected Language: {selected_language}")  # Debugging statement

            # Validate selected language
            if selected_language not in LANGUAGES.keys():
                selected_language = "en"  # Default to English
                error_message = "Invalid language code. Defaulting to English."
                print(f"Selected Language changed to English")  # Debugging statement
            else:
                print(f"Selected Language is valid")  # Debugging statement
                
            video_id = extract_video_id(video_url)

            # Validate video ID extraction
            if not video_id:
                error_message = "Invalid YouTube URL!"
                print(error_message)  # Debugging statement
            else:
                try:
                    print(f"Fetching transcript for video ID: {video_id}")  # Debugging statement
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
                    transcript_text = " ".join([item["text"] for item in transcript])
                    transcript_text = clean_transcript_text(transcript_text)
                    print(f"Cleaned Transcript Text: {transcript_text[:100]}...")  # Debugging statement

                    if transcript_text:
                        print(f"Transcript text 2 lines: {' '.join(transcript_text.splitlines()[:2])}")  # Debugging statement
                        print(f"Transcript Text is done")  # Debugging statement
                    else:
                        error_message = "Error during translation. No output received."
                        print(error_message)  # Debugging statement
                    
                    # Summarize the transcript text
                    try:
                    # Code that generates the summary
                        summary = summarize_text(transcript_text, max_length=200, min_length=75)
                        print(f"Summary 2 lines: {' '.join(summary.splitlines()[:2])}")  # Debugging statement
                    except Exception as e:
                        app.logger.error(f"Error generating summary: {e}")
                        
                    if selected_language != "en":
                        print(f"Selected Language is not English. It is: {selected_language}")  # Debugging statement
                        translated_text = get_translation(summary, selected_language)
                        print(f"Translated Text is ready")  # Debugging statement
                        print(f"Translated Text 2 lines: {' '.join(translated_text.splitlines()[:2])}")  # Debugging statement

                        if translated_text:
                            print(f"Translated text 2 lines: {' '.join(translated_text.splitlines()[:2])}")  # Debugging statement
                        else:
                            error_message = "Error during translation."
                            print(error_message)  # Debugging statement
                    else:
                        translated_text = summary
                        print(f"Transcript Text is kept in English.")  # Debugging statement

                except TranscriptsDisabled:
                    error_message = "Transcripts are disabled for this video."
                    print(error_message)  # Debugging statement
                except Exception as e:
                    error_message = f"Error fetching transcript: {str(e)}"
                    print(error_message)  # Debugging statement
    
    print(f"Final Translated Text is ready")  # Debugging statement
    
    if translated_text:
        print(f"Starting 2 lines of translated text: {' '.join(translated_text[:100])}")  # Debugging statement

    return render_template("index.html", 
                           summary=summary, 
                           translated_text=translated_text,
                           error=error_message, 
                           languages=LANGUAGES, 
                           selected_language=selected_language)

if __name__ == "__main__":
    app.run(debug=True)
