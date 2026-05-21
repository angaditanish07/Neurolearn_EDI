from gtts import gTTS
import os

def generate_number_audio():
    # Create directory if it doesn't exist
    os.makedirs('static/audio/numbers', exist_ok=True)
    
    # Generate audio for numbers 0-10
    for num in range(11):
        tts = gTTS(text=str(num), lang='en', slow=False)
        tts.save(f'static/audio/numbers/{num}.mp3')
        print(f'Generated audio for number {num}')

if __name__ == '__main__':
    generate_number_audio() 