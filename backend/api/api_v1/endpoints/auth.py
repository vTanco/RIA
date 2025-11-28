from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import User
from backend.schemas.api import UserCreate, Token, UserLogin
from backend.core import security
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

from starlette.requests import Request
from backend.core.oauth import oauth

@router.get("/login/{provider}")
async def login_via_provider(provider: str, request: Request):
    redirect_uri = request.url_for('auth_via_provider', provider=provider)
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)

@router.get("/auth/{provider}/callback")
async def auth_via_provider(provider: str, request: Request, db: Session = Depends(get_db)):
    token = await oauth.create_client(provider).authorize_access_token(request)
    user_info = token.get('userinfo')
    
    if not user_info:
        # Fallback for providers that don't return userinfo in token (like Facebook sometimes)
        client = oauth.create_client(provider)
        if provider == 'facebook':
            resp = await client.get('me?fields=id,name,email', token=token)
            user_info = resp.json()
        elif provider == 'github':
             resp = await client.get('user', token=token)
             user_info = resp.json()
             user_info['email'] = user_info.get('email') # Github email might be private

    if not user_info or 'email' not in user_info:
         raise HTTPException(status_code=400, detail="Could not validate credentials")

    # Check if user exists
    user = db.query(User).filter(User.email == user_info['email']).first()
    if not user:
        # Create new user (password is not usable)
        user = User(
            email=user_info['email'],
            hashed_password=security.get_password_hash(security.create_access_token(data={"sub": user_info['email']})) # Random hash
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = security.create_access_token(data={"sub": user.email})
    
    # Redirect to dashboard with token (in a real app, use a secure cookie or intermediate page)
    # For simplicity, we'll return a script to set localStorage and redirect
    from starlette.responses import HTMLResponse
    html_content = f"""
    <html>
        <body>
            <script>
                localStorage.setItem('access_token', '{access_token}');
                window.location.href = '/dashboard.html';
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
