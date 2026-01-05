from package import *

class order_input(BaseModel):
    telegram_id: Optional[Union[str, int]]= None
    email_id: Optional[str] = None
    input_text: str

