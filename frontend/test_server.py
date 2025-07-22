#!/usr/bin/env python3
"""Simple test to verify Flask is working"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Flask is working!</h1>'

if __name__ == '__main__':
    print("Starting test server on http://localhost:9999")
    app.run(host='127.0.0.1', port=9999, debug=False)