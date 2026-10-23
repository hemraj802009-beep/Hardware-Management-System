"""Authentication routes - login, logout."""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import verify_password, create_access_token, get_current_user, hash_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login")
async def login_page(request: Request):
    """Render login page."""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form."""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })
    if not user.is_active:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Account is deactivated"
        })

    token = create_access_token({"sub": user.username, "user_id": user.id, "role": user.role, "name": user.full_name})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=28800)
    return response


@router.get("/signup")
async def signup_page(request: Request):
    """Render signup page."""
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})


@router.post("/signup")
async def signup(
    request: Request,
    full_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process signup form."""
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "Username already taken"
        })
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("signup.html", {
            "request": request,
            "error": "Email already registered"
        })

    new_user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role="staff",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.username, "user_id": new_user.id, "role": new_user.role, "name": new_user.full_name})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=28800)
    return response


@router.get("/logout")
async def logout():
    """Log out the user."""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response
