from package import *
from database import *
from function import *

load_dotenv()

config_postgres_url=os.environ.get("DATABASE_URL")
config_key_jwt = os.environ.get("config_key_jwt")
config_token_expire_sec = int(os.environ.get("config_token_expire_sec",259200))
config_token_user_key_list = "id,user_name,phone_number".split(",")
config_gemini_key = os.environ.get("gemini_key")


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    # This is equivalent to running 'alembic upgrade head' in terminal
    command.upgrade(alembic_cfg, "head")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Running database migrations...")
        #await run_migrations()
        client_postgres = function_client_read_postgres(config_postgres_url)
        client_gemini = function_client_read_gemini(config_gemini_key) if config_gemini_key else None
        app.state.client_postgres = client_postgres
        app.state.config_key_jwt= config_key_jwt
        app.state.config_token_expire_sec= config_token_expire_sec
        app.state.config_token_user_key_list= config_token_user_key_list
        app.state.config_gemini_client=client_gemini
        function_add_app_state({**globals(),**locals()}, app, ("config_","client_","cache_"))
        print("Database connection pool established successfully!")
        yield
    except Exception as e:
        print(f"Failed to establish database connection: {str(e)}")
        print(traceback.format_exc())
    finally:
        if hasattr(app.state, 'client_postgres'):
            app.state.client_postgres.kw['bind'].dispose()
            print("Database connection pool closed.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


router_dir_path = Path(__file__).parent / "router"
function_add_router(app, router_dir_path)


async def function_server_start(app):
    config=uvicorn.Config(app,host="0.0.0.0",port=8000)
    server=uvicorn.Server(config)
    await server.serve()


def function_return_error(message):
   return responses.JSONResponse(status_code=400,content={"status":0,"message":message})


if __name__ == "__main__":
    asyncio.run(function_server_start(app))