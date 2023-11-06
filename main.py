from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
# from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
import json
import requests
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)
import tempfile
# Configure Flask app to connect to the MongoDB
uri = "mongodb+srv://quizdatabase:quiz1234@cluster0.w2xgyzt.mongodb.net?tlsAllowInvalidCertificates=true"  # Change URI as needed

# Initialize PyMongo
mongo = MongoClient(uri)
db = mongo['vps']


@app.route('/')
def index():
    # The homepage will have links to each class page
    return render_template('index.html')


@app.route('/class56')
def class56():
    # Fetch video documents from the class56 collection
    videos = db.class56.find()
    return render_template('class_videos.html', videos=videos, title="Class 5-6 Videos")


@app.route('/class78')
def class78():
    # Fetch video documents from the class78 collection
    videos = db.class78.find()
    return render_template('class_videos.html', videos=videos, title="Class 7-8 Videos")


@app.route('/class910')
def class910():
    # Fetch video documents from the class910 collection
    videos = db.class910.find()
    return render_template('class_videos.html', videos=videos, title="Class 9-10 Videos")

TELEGRAM_BOT_TOKEN = '6989557622:AAHqd788YAvgUqwqsMpes8l60Tg_P1jRXcs'
TELEGRAM_CHAT_ID = '1454652240'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','JPEG','JPG','PNG'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_photo_telegram(image_file_path):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'
    with open(image_file_path, 'rb') as image_file:  # Open the file in binary mode
        files = {'photo': image_file}
        data = {'chat_id': TELEGRAM_CHAT_ID}
        response = requests.post(url, files=files, data=data)
    return response
@app.route('/send_audio', methods=['POST'])
def send_audio():
    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_audio:
        audio_file.save(temp_audio)
        temp_audio_path = temp_audio.name
    response = send_audio_telegram(temp_audio_path)
    os.remove(temp_audio_path)  # Clean up the temporary file
    return jsonify(response.json())

def send_audio_telegram(audio_file_path):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio'
    with open(audio_file_path, 'rb') as audio:  # Open the file in binary mode
        files = {'audio': audio}
        data = {'chat_id': TELEGRAM_CHAT_ID}
        response = requests.post(url, files=files, data=data)
    return response

def send_document_telegram(image_file_path):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument'
    with open(image_file_path, 'rb') as document_file:  # Open the file in binary mode
        files = {'document': document_file}
        data = {'chat_id': TELEGRAM_CHAT_ID}
        response = requests.post(url, files=files, data=data)
    return response

@app.route('/send_doubt', methods=['POST'])
def send_doubt():
    if 'doubt_photo' not in request.files:
        # Handle the case where the file part is missing
        return redirect(url_for('index'))
    file = request.files['doubt_photo']
    if file.filename == '':
        # Handle the case where no file was selected
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join('static', filename)  # Use os.path.join for OS-independent paths
        file.save(file_path)
        print(file_path)
        send_photo_telegram(file_path)
        send_document_telegram(file_path)
        os.remove(file_path)  # Make sure to remove the file after processing
        return redirect(url_for('index'))

@app.route('/admin/create')
def admin_create():
    return render_template('admin_create.html')

@app.route('/admin/add_video', methods=['POST'])
def add_video():
    collection_name = request.form['collection']
    title = request.form['title']
    vdo_id = request.form['vdo_id']
    des = request.form['des']
    collection = db[collection_name]
    collection.insert_one({'title': title, 'vdo_id': vdo_id, 'des': des})
    return redirect(url_for('admin_create'))

@app.route('/admin/list')
def admin_list():
    return render_template('admin_list.html')

@app.route('/admin/get_videos', methods=['POST'])
def get_videos():
    collection_name = request.form['collection']
    documents = list(db[collection_name].find({}, {'title': 1, 'vdo_id': 1, 'des': 1}))
    return render_template('admin_list_docs.html', documents=documents, collection_name=collection_name)

@app.route('/admin/delete_video/<collection_name>/<video_id>')
def delete_video(collection_name, video_id):
    db[collection_name].delete_one({'_id': ObjectId(video_id)})
    return redirect(url_for('admin_list'))



# Run Flask app
if __name__ == '__main__':
    app.run(debug=False)
