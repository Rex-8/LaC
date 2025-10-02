from flask import Flask, request, jsonify, render_template, render_template_string
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

STEP1_PROMPT = """You are an AI for an e-commerce app. Generate SQL query for user request.

DATABASE SCHEMA:
- products: id, name, description, price, color, category, image_url, stock
- cart: id, user_id, product_id, quantity, size, added_at
- orders: id, user_id, total_amount, status, shipping_address, created_at
- order_items: id, order_id, product_id, quantity, size, price

USER_ID: {user_id}

RULES:
- Expand user search terms to include synonyms, plurals, and semantically related product categories/items 
  (e.g., if "jacket" is asked, include jackets, hoodies, coats, sweatshirts, t-shirts if relevant).
- Use LIKE with wildcards or category-based filtering to capture variations.
- ALWAYS use user_id = {user_id} for cart/orders
- Return ONLY valid SQL query, nothing else

USER REQUEST: {user_message}

SQL QUERY:"""

STEP2_PROMPT = """You generated SQL and got results. Now create a Jinja2 template.

USER REQUEST: {user_message}
SQL EXECUTED: {sql_query}
RESULTS COUNT: {result_count} rows
SAMPLE DATA: {sample_data}

CSS CLASSES:
- product-grid, product-card, product-image, product-info, product-price, add-btn
- cart-summary, cart-item, cart-total
- checkout-form, form-group, submit-btn

RETURN JSON:
{{
  "message": "conversational response",
  "template": "Jinja2 template using {{% for item in data %}} loops"
}}

TEMPLATE RULES:
- Use {{% for item in data %}} for iteration
- Access fields: {{{{ item.name }}}}, {{{{ item.price }}}}
- For forms: use onsubmit="event.preventDefault(); addToCart({{{{ item.id }}}}, this);"
- Include size/quantity inputs in forms
- NO <script> tags
- Return ONLY JSON"""

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
    
    print("\n" + "="*80)
    print("🔵 USER MESSAGE")
    print("="*80)
    print(f"Message: {user_message}")
    
    try:
        # STEP 1: Generate SQL
        print("\n" + "="*80)
        print("STEP 1: GENERATING SQL")
        print("="*80)
        
        step1_prompt = STEP1_PROMPT.format(user_id=user_id, user_message=user_message)
        response1 = model.generate_content(step1_prompt)
        sql_query = response1.text.strip()
        
        # Clean markdown
        if sql_query.startswith('```'):
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        print(f"SQL: {sql_query}")
        
        # Validate and execute SQL
        is_valid, error = validate_sql(sql_query, user_id)
        if not is_valid:
            print(f"❌ VALIDATION FAILED: {error}")
            return jsonify({"error": error}), 400
        
        result = execute_query(sql_query)
        if not result['success']:
            print(f"❌ QUERY FAILED: {result['error']}")
            return jsonify({"error": result['error']}), 500
        
        query_data = result.get('data', [])
        print(f"✅ Got {len(query_data)} rows")
        
        # STEP 2: Generate template based on results
        print("\n" + "="*80)
        print("STEP 2: GENERATING TEMPLATE")
        print("="*80)
        
        sample_data = query_data[:3] if query_data else []
        step2_prompt = STEP2_PROMPT.format(
            user_message=user_message,
            sql_query=sql_query,
            result_count=len(query_data),
            sample_data=json.dumps(sample_data, indent=2)
        )
        
        response2 = model.generate_content(step2_prompt)
        llm_response = response2.text.strip()
        
        if llm_response.startswith('```'):
            llm_response = llm_response.replace('```json', '').replace('```', '').strip()
        
        llm_data = json.loads(llm_response)
        print(f"Template generated")
        
        # Render template with data
        rendered_html = ""
        if 'template' in llm_data and llm_data['template']:
            template = llm_data['template']
            print(f"Template: {template[:200]}...")
            rendered_html = render_template_string(template, data=query_data, user_id=user_id)
            print(f"✅ Rendered {len(rendered_html)} chars")
        
        print("="*80)
        
        return jsonify({
            "message": llm_data.get('message', ''),
            "html": rendered_html
        })
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)