from package import *

# Dependency to get a DB session per request
def get_db(request: Request):
    # Access the factory stored in app.state
    session_factory = request.app.state.client_postgres
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

    return None

def function_add_app_state(var_dict,app,prefix_tuple):
    for k, v in var_dict.items():
        if k.startswith(prefix_tuple):
            setattr(app.state, k, v)

def function_add_router(app, router_folder_path):
    router_root = Path(router_folder_path).resolve()
    if not router_root.is_dir():
        raise ValueError(f"router folder not found: {router_root}")
    def load_module(file_path):
        try:
            rel = file_path.relative_to(router_root)
            module_name = "routers." + ".".join(rel.with_suffix("").parts)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            if hasattr(module, "router"):
                app.include_router(module.router)
        except Exception:
            print(f"[WARN] failed to load router: {file_path}")
            traceback.print_exc()
    for file_path in router_root.rglob("*.py"):
        if not file_path.name.startswith("__"):
            load_module(file_path)
    return None


async def function_token_encode(config_key_jwt,config_token_expire_sec,object,user_key_list):
    data=dict(object)
    payload={k:data.get(k) for k in user_key_list}
    payload=json.dumps(payload,default=str)
    token=jwt.encode({"exp":time.time() + config_token_expire_sec,"data":payload},config_key_jwt)
    return token

async def function_token_decode(token,config_key_jwt):
    user=json.loads(jwt.decode(token,config_key_jwt,algorithms="HS256")["data"])
    return user

# from openai import OpenAI
# def function_client_read_gemini(config_gemini_key):
#     client_gemini=OpenAI(api_key=config_gemini_key,base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
#     return client_gemini

from google import genai
def function_client_read_gemini(config_gemini_key):
    # No base_url needed; the SDK handles routing to Google's servers automatically.
    client_gemini = genai.Client(api_key=config_gemini_key)
    return client_gemini