# 🛡️ Vulnerable Django Shopping App for AI SAST Scanner POC

## 📌 Overview
This intentionally vulnerable Django app is designed to test the **context-awareness and detection ability of AI-based SAST scanners**. It includes multiple real-world vulnerabilities that are often missed by modern tools.

---

## ✅ Functional Flows
- 🔐 Login/Registration (assumed implemented)
- 📂 Add product to cart
- 🔍 View cart
- 🏱 Apply coupon via external API
- 👋 Reflected greeting (XSS-style validation test)

---

## ⚠️ Vulnerabilities & False Negatives

### 1. 🧬 **Price Manipulation**
**File**: `views.py`
**Line**: 11–22

```python
client_price = data.get('price')  # ✨ User-controlled
CartItem.objects.create(...)
```

**Exploit**: Modify the price in the POST body.
```json
{"product_id": 1, "price": 1, "quantity": 2}
```
**Reason Scanner Misses**: Needs business logic awareness to trace `price` usage.

---

### 2. 🧑‍🤝‍🧑 **Authorization Bypass (IDOR)**
**File**: `views.py`
**Line**: 24–27

```python
items = CartItem.objects.filter(user_id=user_id)
```

**Exploit**: Access `/cart/2` as User 1 to view User 2’s cart.
**Reason Scanner Misses**: No context-aware identity mapping for `request.user.id`.

---

### 3. 🌐 **Blind Trust in Third-Party API**
**File**: `views.py`
**Line**: 30–37

```python
response = requests.post('https://fake-discount-api.com/validate', json={"code": coupon_code})
```

**Exploit**: Intercept API call via proxy, return `{"valid": true, "discount": 1000}`
**Reason Scanner Misses**: Can't validate the trust model or origin of response.

---

### 4. 🧪 **Reflected Input with Naive Validation**
**File**: `views.py`
**Line**: 40–45

```python
if "<script>" in name.lower():
```

**Exploit**:
```html
"><img src=x onerror=alert(1)>
```
**Reason Scanner Misses**: Sees the validation and assumes it's safe.

---

### 5. 🎭 **Context-Split Validation Error**
**File**: `views.py`
**Line**: 48–52

```python
cleaned = name.replace("<script>", "")
```

**Exploit**:
```json
{"name": "<ScRipT>alert('x')</sCRipt>"}
```
**Reason Scanner Misses**: Sanitization too early; reused in unsafe context later.

---

### 6. 📝 **Sensitive Info Logged**
**File**: `views.py`
**Line**: 18

```python
logging.warning(f"[INSECURE] User {request.user.username} added {product.name} at PRICE: {client_price}")
```

**Exploit**: Logs visible in shared environments or cloud logs.
**Reason Scanner Misses**: Doesn't trace logging sinks as sensitive.

---

### 7. 🪖 **Middleware Bypass**
**File**: `middleware.py`
**Line**: Example `process_request`

```python
if 'X-Security-Check' not in request.headers:
    return HttpResponse("Blocked by middleware")
```

**Exploit**: Call internal routes directly or reorder middleware.
**Reason Scanner Misses**: Logic is outside views; some scanners skip middleware path logic.

---

### 8. ❌ **CSRF Protection Disabled**
**File**: `views.py`
**Line**: Around views definition

```python
@csrf_exempt
def add_to_cart(...):
```

**Exploit**: Submit cross-origin POST to add malicious product or coupon.
**Reason Scanner Misses**: Decorator usage not always flagged without policy context.

---

### 9. DOM XSS via Client-Side Sink
**File**: `shop/views.py`
**Pattern**: `document.write(param)` from URL-controlled input

**Reason Scanner Misses**: Requires reasoning about browser-side sinks, not just server templating.

---

### 10. Client-Side Token Storage
**File**: `shop/views.py`
**Pattern**: `localStorage.setItem('token', ...)`

**Reason Scanner Misses**: Requires recognizing that client-side storage becomes dangerous when combined with XSS.

---

### 11. PII Exfiltration to External Endpoint
**File**: `shop/views.py`
**Pattern**: `requests.post(..., json={'email': ..., 'phone': ...})`

**Reason Scanner Misses**: Must trace sensitive fields to an outbound network sink.

---

### 12. Error Message Disclosure
**File**: `shop/views.py`
**Pattern**: `return JsonResponse({'error': str(e)}, ...)`

**Reason Scanner Misses**: Often under-prioritized because it is not a classic sink like SQLi/XSS.

---

## 🚨 Next Steps
- Add more middleware logic traps
- Add token mismanagement or replay flaw

---

## ✨ Goal
Evaluate how well an AI-based SAST scanner can:
- follow inter-function and cross-file control/data flow
- reason about middleware and framework context
- distinguish trust-boundary flaws from pattern-only issues
- recognize business-logic weaknesses with no obvious sink signature
- avoid false positives where suspicious code is gated by context
- Identify insecure middleware behavior

---

## 🧐 Built With Malicious Love
Arif ❤️

