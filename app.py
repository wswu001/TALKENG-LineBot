import io
from copy import deepcopy
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    AudioMessageContent,
)
from transformers import pipeline
from pydub import AudioSegment
from transformers import Wav2Vec2Tokenizer, Wav2Vec2ForCTC
import librosa
import soundfile as sf
import torch
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)  # app is a web server

# Tokens and secrets managed via environment variables
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("LINE_ACCESS_TOKEN or LINE_CHANNEL_SECRET not set in environment variables")

configuration = Configuration(access_token=LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
translator = pipeline("translation", model='Helsinki-NLP/opus-mt-zh-en')

tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# Callback route
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# Text message handling
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    msg_text = event.message.text

    # Translation: Chinese to English
    if msg_text.startswith("\en"):
        msg_text = msg_text.replace("\en", "")
        en = translator(msg_text)[0]['translation_text']
        f = TextMessage(text="[EN] " + en)
    else:
        f = TextMessage(text=msg_text)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[f]
            )
        )


# Audio message handling
@handler.add(MessageEvent, message=AudioMessageContent)
def handle_content_message(event):
    with ApiClient(configuration) as api_client:
        # line message
        line_bot_blob_api = MessagingApi(api_client)
        msg_audio_binary = line_bot_blob_api.get_message_content(message_id=event.message.id)

        audio_buffer = io.BytesIO(msg_audio_binary)
        audio_segment = AudioSegment.from_file(audio_buffer, format='m4a')
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        audio_input, sample_rate = sf.read(wav_buffer)

        if len(audio_input.shape) > 1:
            audio_input = audio_input.mean(axis=1)
        if sample_rate != 16000:
            audio_input = librosa.resample(audio_input, orig_sr=sample_rate, target_sr=16000)
            sample_rate = 16000

        # Tokenize the audio input
        input_values = tokenizer(audio_input, return_tensors="pt", padding="longest", sampling_rate=sample_rate).input_values

        # Perform the transcription
        with torch.no_grad():
            logits = model(input_values).logits

        # Decode the logits to text
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = tokenizer.batch_decode(predicted_ids)[0]

        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f'{transcription}')]
            )
        )


if __name__ == "__main__":
    app.run(port=4000)
