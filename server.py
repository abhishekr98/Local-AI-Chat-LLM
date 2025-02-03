from flask import Flask, request, jsonify, send_from_directory, render_template
import requests
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Ollama configuration
OLLAMA_API_URL = "http://localhost:11434/api/chat"  # Ollama's local API endpoint

# Route to serve index.html from the 'templates' folder
@app.route('/')
def index():
    return render_template('index.html')  # This assumes 'index.html' is in the 'templates' folder

@app.route('/clear', methods=['POST'])
def clear_chat():
    return jsonify({"status": "success"})


# Route to handle the chatbot's responses
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('messages', [])
    if not user_input:
        return jsonify({'error': 'Message history is required'}), 400

    # Prepare the payload to send to Ollama
    payload = {
        "model": "llama3.2",  # Use the model you've pulled into Ollama
        "messages": user_input  # Send the entire message history
    }

    try:
        # Send the POST request to Ollama's API with streaming enabled
        response = requests.post(OLLAMA_API_URL, json=payload, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Initialize variable for the final content
        final_reply = ""

        # Iterate over the response stream
        for chunk in response.iter_lines():
            if chunk:
                # Decode and process the chunk as a JSON object
                try:
                    chunk_data = json.loads(chunk.decode('utf-8'))
                    # Collect the content if the 'message' key exists in the chunk
                    if 'message' in chunk_data:
                        final_reply += chunk_data['message']['content']
                except json.JSONDecodeError as e:
                    print("Error parsing chunk JSON:", e)

        # Return the final response to the frontend
        return jsonify({'reply': final_reply})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# Optional: Serve static files like CSS and JS if needed
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(os.getcwd(), 'static'), path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run on all interfaces
