"""Web routes - home page."""

from flask import Blueprint

bp = Blueprint('web', __name__)


@bp.route('/')
def home():
    return """<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>गीता GPT 🙏</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        h1 { font-size: 2.5rem; margin-bottom: 10px; }
        p { color: #555; font-size: 1.1rem; margin-bottom: 20px; line-height: 1.6; }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 30px;
            text-decoration: none;
            font-size: 1.2rem;
            margin: 10px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: scale(1.05); }
        .api-info {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: left;
            font-size: 0.9rem;
            color: #888;
        }
        code {
            background: #f0f0f0;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>🙏 गीता GPT</h1>
        <p>भगवद्गीता के ज्ञान से जीवन के प्रश्नों का उत्तर</p>
        <p>Telegram पर बात करें 👇</p>
        <a class="btn" href="https://t.me/GitaGPTBot">Telegram Bot खोलें</a>

        <div class="api-info">
            <p><strong>API:</strong></p>
            <p><code>GET /ask?q=your question</code></p>
            <p><code>GET /shloka/2.47</code></p>
            <p><code>GET /health</code></p>
        </div>
    </div>
</body>
</html>"""
