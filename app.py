from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import json
import os
from database import execute_query
from guardrails import validate_sql, sanitize_html

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

SYSTEM_PROMPT = """You are an AI backend with direct database access for an e-commerce app.

DATABASE SCHEMA:
- products: id, name, description, price, color, category, image_url, stock
- cart: id, user_id, product_id, quantity, size, added_at
- orders: id, user_id, total_amount, status, shipping_address, created_at
- order_items: id, order_id, product_id, quantity, size, price

AVAILABLE CSS CLASSES:
- product-grid, product-card, product-image, product-info, product-price, add-btn
- cart-summary, cart-item, cart-total
- checkout-form, form-group, submit-btn

YOUR JOB:
1. Generate SQL queries to handle user requests
2. Generate HTML using CSS classes above
3. Return valid JSON ONLY

RESPONSE FORMAT (MUST BE VALID JSON):
{
  "message": "conversational response",
  "sql": "SELECT * FROM products WHERE...",
  "html": "<div class='product-grid'>...</div>"
}

RULES:
- ALWAYS use user_id = {user_id} for cart/orders queries
- Generate complete valid SQL
- Embed actual data in HTML (don't use placeholders)
- For cart operations, include data-product-id and data-size attributes on buttons
- Make HTML interactive with onclick handlers where needed
- RETURN ONLY JSON, NO MARKDOWN, NO EXTRA TEXT
"""

conversation_history = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    user_id = data.get('user_id', 1)
    session_id = data.get('session_id', 'default')
    
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    full_prompt = SYSTEM_PROMPT.replace('{user_id}', str(user_id))
    full_prompt += f"\n\nCONVERSATION HISTORY:\n"
    for msg in conversation_history[session_id][-5:]:
        full_prompt += f"{msg['role']}: {msg['content']}\n"
    full_prompt += f"\nUSER MESSAGE: {user_message}\n\nRESPOND WITH JSON ONLY:"
    
    try:
        response = model.generate_content(full_prompt)
        assistant_message = response.text.strip()
        
        if assistant_message.startswith('```json'):
            assistant_message = assistant_message.replace('```json', '').replace('```', '').strip()
        elif assistant_message.startswith('```'):
            assistant_message = assistant_message.replace('```', '').strip()
        
        conversation_history[session_id].append({
            "role": "user",
            "content": user_message
        })
        conversation_history[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        try:
            llm_data = json.loads(assistant_message)
        except:
            return jsonify({
                "message": assistant_message,
                "html": ""
            })
        
        result_html = ""
        sql_executed = []
        
        if 'sql' in llm_data and llm_data['sql']:
            queries = llm_data['sql'] if isinstance(llm_data['sql'], list) else [llm_data['sql']]
            
            for query in queries:
                is_valid, error = validate_sql(query, user_id)
                if not is_valid:
                    return jsonify({"error": error}), 400
                
                result = execute_query(query)
                sql_executed.append({
                    "query": query,
                    "result": result
                })
                
                if not result['success']:
                    return jsonify({"error": result['error']}), 500
        
        if 'html' in llm_data and llm_data['html']:
            result_html = sanitize_html(llm_data['html'])
        
        return jsonify({
            "message": llm_data.get('message', ''),
            "html": result_html,
            "sql_executed": sql_executed
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)