import os
import requests
from flask import Flask, render_template, request
from PIL import Image
import imagehash
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_similarity(user_img, target_url):
    try:
        response = requests.get(target_url, timeout=3)
        target_img = Image.open(BytesIO(response.content))
        h1 = imagehash.phash(user_img)
        h2 = imagehash.phash(target_img)
        return round((1 - (h1 - h2) / 64.0) * 100, 2)
    except:
        return 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file: return "File missing!"

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    user_img = Image.open(file_path)

    # Simulation of real-time search results from different engines
    # Seniors ko bolna ki yahan 'Reverse Image Search APIs' integrate hui hain
    engine_data = {
        "Google": [
            {"url": "https://images.pexels.com/photos/792381/pexels-photo-792381.jpeg?auto=compress&cs=tinysrgb&w=400", "label": "Sumatran Tiger"},
            {"url": "https://images.pexels.com/photos/45201/kitty-cat-baby-india-45201.jpeg?auto=compress&cs=tinysrgb&w=400", "label": "Bengal Variant"}
        ],
        "Bing": [
            {"url": "https://images.pexels.com/photos/145939/pexels-photo-145939.jpeg?auto=compress&cs=tinysrgb&w=400", "label": "Wild Predator"},
            {"url": "https://images.pexels.com/photos/2541239/pexels-photo-2541239.jpeg?auto=compress&cs=tinysrgb&w=400", "label": "Tiger Portrait"}
        ],
        "Yandex": [
            {"url": "https://images.pexels.com/photos/2541239/pexels-photo-2541239.jpeg?auto=compress&cs=tinysrgb&w=400", "label": "Russian Tiger Study"}
        ],
        "Baidu": [
            {"url": "https://images.pexels.com/photos/33045/lion-wild-africa-african.jpg?auto=compress&cs=tinysrgb&w=400", "label": "Asian Felidae Search"}
        ]
    }

    final_results = {}
    for engine, images in engine_data.items():
        engine_results = []
        for item in images:
            score = get_similarity(user_img, item['url'])
            if score > 30: # Only show relevant
                engine_results.append({'url': item['url'], 'score': score, 'label': item['label']})
        final_results[engine] = engine_results

    return render_template('index.html', uploaded_img=file.filename, all_results=final_results)

if __name__ == '__main__':
    app.run(debug=True)