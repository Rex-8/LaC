import re

def validate_sql(query, user_id):
    query_upper = query.upper()
    
    forbidden = ['DROP', 'ALTER', 'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE']
    for keyword in forbidden:
        if keyword in query_upper:
            return False, f"Forbidden operation: {keyword}"
    
    if 'DELETE FROM PRODUCTS' in query_upper:
        return False, "Cannot delete products"
    
    if 'CART' in query_upper or 'ORDERS' in query_upper or 'ORDER_ITEMS' in query_upper:
        if f'user_id = {user_id}' not in query.lower() and f'user_id={user_id}' not in query.lower():
            return False, "Must include user_id constraint"
    
    return True, "OK"

def sanitize_html(html):
    forbidden_tags = ['<script', '<iframe', 'javascript:', 'onerror=', 'onload=']
    for tag in forbidden_tags:
        if tag.lower() in html.lower():
            return ""
    return html