from package import *
from database import *

class Order(Base):
    __tablename__ = "orders"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )

    telegram_chat_id = Column(String, index=True, nullable=True)
    email_id = Column(String,nullable=True)

    raw_input_text = Column(String, nullable=False)
    
    extracted_specs = Column(JSONB, default=dict)
    pricing_breakdown = Column(JSONB, default=dict)

    final_price = Column(Float, nullable=True)

    status = Column(
        String,
        default="received",
        index=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False
    )