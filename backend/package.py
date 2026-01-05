from fastapi import FastAPI
import uvicorn
import os
import dotenv
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager
import traceback
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from fastapi import responses
import sys
import importlib.util
from pathlib import Path
import hashlib
# from fastapi import HTTPException 
from http_exceptions import HTTPException


from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from fastapi import Depends, Request

from typing import Optional
from pydantic import BaseModel, Field
import jwt
import json,time
from fastapi import HTTPException, status
import bcrypt
from fastapi import APIRouter, Request, Depends, Query

from sqlalchemy import desc, case
from sqlalchemy import func, case, or_
from sqlalchemy.orm import Session

from enum import Enum
from typing import Union, Optional
from fastapi.responses import HTMLResponse