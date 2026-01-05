from package import *
from database import *


class Employee(Base):
    __tablename__ = "Employee"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False
    )
    
    organisation = Column(String,nullable=False)
    name = Column(String,nullable=False)
    
    role = Column(String,nullable=False)
    email_id = Column(String,nullable=False)
    
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