from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

browser_events = []


@app.route('/event', methods=['POST'])
def receive_event():
    data = request.json
    data['received_at'] = datetime.now().isoformat()
    browser_events.append(data)
    tag = data.get('element', {}).get('tag', data.get('tag', '?'))
    text = data.get('element', {}).get('text', data.get('text', ''))[:30]
    url = data.get('url', '')[:50]
    print(f"[BROWSER] {tag} - {text} @ {url}")
    return jsonify({"status": "ok"})


@app.route('/events', methods=['GET'])
def get_events():
    return jsonify(browser_events)


@app.route('/events', methods=['DELETE'])
def clear_events():
    browser_events.clear()
    return jsonify({"status": "cleared"})


def run_server():
    app.run(host='127.0.0.1', port=8000, threaded=True)


if __name__ == '__main__':
    run_server()
