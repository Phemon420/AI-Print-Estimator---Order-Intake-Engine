from services.order import *
from schema.order import order_input
from schema.escalate import status_update
from package import *
from main import *

@app.get("/")
async def function_api_root():
   return {"status":1,"message":"API is working!"}

@app.post("/input/order")
async def function_api_auth_signup(request:Request,orders:order_input):
    print("here error is not present")
    if orders.email_id:
        output=await order_analysis(request.app.state.config_gemini_client,request.app.state.client_postgres,orders.input_text,"email",orders.email_id)
    elif orders.telegram_id:
        output=await order_analysis(request.app.state.config_gemini_client,request.app.state.client_postgres,orders.input_text,"telegram",orders.telegram_id)
    else:
        raise HTTPException(status=400,message="no id is provided")
    return output

@app.post("/escalation")
async def function_api_escalation(request:Request,status_update:status_update):
    try:
        return await order_escalation(request.app.state.config_gemini_client, request.app.state.client_postgres, status_update.order_id, status_update.status_level)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while executing escalation: {e}")
    
@app.post("/escalation/workflow")
async def function_api_escalation(request:Request,status_update:status_update):
    try:
        return await order_escalation_workflow(request.app.state.config_gemini_client, request.app.state.client_postgres, status_update.order_id, status_update.status_level)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while executing escalation: {e}")
    
    
@app.get("/review-form", response_class=HTMLResponse)
async def serve_review_form(order_id: str, current_level: str):
    return f"""
    <html>
        <head>
            <style>
                body {{ font-family: sans-serif; display: flex; justify-content: center; padding: 50px; background: #f4f4f9; }}
                .card {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 400px; }}
                .btn-group {{ display: flex; flex-direction: column; gap: 10px; margin-top: 20px; }}
                button {{ padding: 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; color: white; }}
                .btn-escalate {{ background: #ff9800; }}
                .btn-accept {{ background: #4caf50; }}
                .btn-reject {{ background: #f44336; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Order Review</h2>
                <p>Order ID: <strong>{order_id}</strong></p>
                <p>Status: <strong>{current_level}</strong></p>
                
                <div class="btn-group">
                    <button onclick="sendUpdate('{order_id}', '{current_level}')" class="btn-escalate">🚀 Escalate</button>
                    <button onclick="sendUpdate('{order_id}', 'level_5')" class="btn-accept">✅ Accept</button>
                    <button onclick="sendUpdate('{order_id}', 'level_7')" class="btn-reject">❌ Reject</button>
                </div>
                <p id="response-msg" style="margin-top:15px; font-weight: bold;"></p>
            </div>

            <script>
                // FIX: Changed 'async def' to 'async function'
                async function sendUpdate(orderId, level) {{
                    const responseMsg = document.getElementById('response-msg');
                    responseMsg.innerText = "⏳ Processing...";
                    responseMsg.style.color = "black";

                    try {{
                        const response = await fetch('/escalation/workflow', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ 
                                order_id: orderId, 
                                status_level: level 
                            }})
                        }});

                        const result = await response.json();
                        
                        if (response.ok) {{
                            responseMsg.style.color = "green";
                            responseMsg.innerText = "✅ Success! Action completed.";
                        }} else {{
                            responseMsg.style.color = "red";
                            responseMsg.innerText = "❌ Error: " + (result.detail || "Unknown error");
                        }}
                    }} catch (err) {{
                        responseMsg.style.color = "red";
                        responseMsg.innerText = "❌ Connection failed. Is the server running?";
                        console.error(err);
                    }}
                }}
            </script>
        </body>
    </html>
    """