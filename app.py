from flask import Flask, request, jsonify, render_template, redirect, url_for
import joblib
import json
import os
from datetime import datetime
from flask_cors import CORS
import csv

app = Flask(__name__)
CORS(app)

model = joblib.load('spam_detector_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')
LOG_FILE = 'logs.json'

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        json.dump([], f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    email_text = data.get("email")

    if not email_text:
        return jsonify({"error": "No email text provided."}), 400

    try:
        vectorized_text = vectorizer.transform([email_text])
        prediction = model.predict(vectorized_text)[0]
        result = "Spam" if prediction == 1 else "Not Spam"

        log_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": result,
            "text": email_text
        }
        with open(LOG_FILE, 'r+') as f:
            logs = json.load(f)
            logs.append(log_entry)
            f.seek(0)
            json.dump(logs, f, indent=4)

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)

    spam_count = sum(1 for log in logs if log["result"] == "Spam")
    not_spam_count = sum(1 for log in logs if log["result"] == "Not Spam")

    return render_template('dashboard.html', logs=logs, spam_count=spam_count, not_spam_count=not_spam_count)

@app.route('/delete', methods=['POST'])
def delete_entry():
    timestamp_to_delete = request.form.get("timestamp")

    if not timestamp_to_delete:
        return "Timestamp missing", 400

    try:
        with open(LOG_FILE, 'r+') as f:
            logs = json.load(f)
            logs = [log for log in logs if log["timestamp"] != timestamp_to_delete]
            f.seek(0)
            f.truncate()
            json.dump(logs, f, indent=4)
        return redirect('/dashboard')
    except Exception as e:
        return f"Error deleting entry: {str(e)}", 500


@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    with open(LOG_FILE, 'w') as f:
        json.dump([], f)
    return redirect(url_for('dashboard'))

@app.route('/export_logs')
def export_logs():
    with open(LOG_FILE, 'r') as f:
        logs = json.load(f)

    csv_file = 'static/exported_logs.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "result", "text"])
        writer.writeheader()
        writer.writerows(logs)

    return redirect(url_for('static', filename='exported_logs.csv'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)