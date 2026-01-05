from model.order import Order as model_order
from model.Employee import Employee
from schema.order import order_input
from package import *
import httpx

STATUS={
    "level_1":"received",
    "level_2":"CSR_Review",
    "level_3":"CSR_Review_Manager",
    "level_4":"CSR_Review_Senior_Manager",
    "level_5":"MIS_Handoff",
    "level_6":"executed",
    "level_7":"impossible"
}

async def order_analysis(client_gemini,db_store,extracted_text,id_type,client_id):
    db: Session = db_store()
    try:
        response_schema = {
            "type": "object",
            "properties": {
                "quantity": {"type": "integer", "nullable": False},
                "width": {"type": "number", "nullable": False},
                "height": {"type": "number", "nullable": False},
                "paper_type": {"type": "string", "nullable": False},
                "is_rush": {"type": "boolean"},
                "price": {"type":"integer", "nullable":False}
            },
            "required": ["quantity","width","is_rush","height","paper_type","price"]
        }

        # 2. Configure Generation (Strict Output, No Streaming)
        generation_config = {
            "response_mime_type": "application/json",
            "response_schema": response_schema,
        }

        # 3. Call Gemini
        prompt = f"**important**:if sufficient data not present return empty values for the fields do not assume anything by yourself always ask back if the info does not give exact values but specifies such that those values can be calculated then it is fine else ask and make sure to take measurement in centimeter do not make any assumption when it comes to size and quantity especially always return them empty in this case. Extract structured print specifications from the following user request: {extracted_text} and fill in the details according to you and market price for each stuff as availaible online only write the price of one product in price tag not multiple just a single unit price give me that i will do the further calculations myself give response in rupee indian currency. "
        
        response = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=generation_config
        )

        # 4. Parse Structured Data
        structured_data = json.loads(response.text)

        def is_missing(value):
            return value in (None, "", 0)

        if is_missing(structured_data.get("quantity")):
            return {"status_code":405,"detail":"Product quantity is missing"}
        
        if is_missing(structured_data.get("paper_type")):
            return {"status_code":405,"detail":"Product quality is missing"}

        if is_missing(structured_data.get("height")) or is_missing(structured_data.get("width")):
            return {"status_code":405,"detail":"Product measurement is missing"}
            
        current_status = "Wait_For_Review"
        print(structured_data)
        # Basic math: ($0.10 per unit + $15 setup)
        total = (structured_data["quantity"] * structured_data["price"]) + 15.0
        pricing = {
            "subtotal": total,
            "tax": total * 0.08,
            "total_price": total * 1.08
        }

        structured_data["price"]=pricing["total_price"]
        # 6. Database Persistence
        # Using your model_order from the model.order import
        new_order = model_order(
            telegram_chat_id=client_id if id_type == "telegram" else None,
            email_id=client_id if id_type=="email" else None,
            raw_input_text=extracted_text,
            extracted_specs=structured_data,
            pricing_breakdown=pricing,
            final_price=pricing.get("total_price"),
            status=current_status
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        return {"status_code":200,"message":structured_data,"order_id":new_order.id}

    except Exception as e:
        db.rollback()
        raise e
        # raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()



async def order_escalation(client_gemini,db_store,order_id,status_level):
    db: Session = db_store()
    try:
        order=db.get(model_order,order_id)
        if order:
            order.status=STATUS[status_level]
        
        order.status = STATUS.get(status_level)
        level_num=int(status_level[-1])
        print(level_num)
        if status_level in ("level_2", "level_3", "level_4"):

            role_needed = STATUS[status_level]

            approver: Employee = (db.query(Employee).filter(Employee.role == role_needed).first())

            if not approver:
                raise RuntimeError(
                    f"No approver found for role={role_needed} "
                )

            order.email_id = approver.email_id
            db.commit()

            return  {
                        "order_id": str(order.id),
                        "status_level": f"level_{level_num+1}",
                        "approver_email": approver.email_id,
                        "role": role_needed,
                        "order_request":order.raw_input_text,
                        "extracted_specs":order.extracted_specs
                    }

        elif status_level == "level_5":
            order.status = STATUS["level_6"]
            db.commit()
            owner: Employee = (db.query(Employee).filter(Employee.role == "MIS_Handoff").first())
            return { "order_id": str(order.id), "status":"done and dusted","email":owner.email_id } 

        else:
            db.delete(order)
            db.commit()
            return {"order_id": str(order.id), "status": "removed"}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
        

async def order_escalation_workflow(client_gemini, db_store, order_id, status_level):
    db: Session = db_store()
    n8n_webhook_url = "https://taking-lcd-phoenix-optional.trycloudflare.com/webhook-test/lol"
    
    try:
        order = db.get(model_order, order_id)
        if order:
            order.status = STATUS.get(status_level)
        
        level_num = int(status_level[-1])
        
        # Logic to determine response data
        if status_level in ("level_2", "level_3", "level_4"):
            role_needed = STATUS[status_level]
            approver: Employee = (db.query(Employee).filter(Employee.role == role_needed).first())
            if not approver:
                raise RuntimeError(f"No approver found for role={role_needed}")

            order.email_id = approver.email_id
            db.commit()

            payload = {
                "order_id": str(order.id),
                "status": f"level_{level_num+1}",
                "email": approver.email_id,
                "role": role_needed,
                "order_request":order.raw_input_text,
                "extracted_specs":order.extracted_specs
            }

        elif status_level == "level_5":
            order.status = STATUS["level_6"]
            db.commit()
            owner: Employee = (db.query(Employee).filter(Employee.role == "MIS_Handoff").first())
            payload = { "order_id": str(order.id), "status": "done and dusted", "email": owner.email_id } 

        else:
            db.delete(order)
            db.commit()
            payload = {"order_id": str(order.id), "status": "removed"}

        try:
            async with httpx.AsyncClient() as client:
                await client.get(n8n_webhook_url, params=payload, timeout=5.0)
        except Exception as n8n_err:
            print(f"n8n Trigger Failed: {n8n_err}")

        return payload

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()