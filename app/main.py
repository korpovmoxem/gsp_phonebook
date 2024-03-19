import json
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Request, HTTPException, status, Form, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sql_server_connector import DataBaseStorage
from authentication import ActiveDirectoryConnection, CookieUserName


app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')


phonebook_data = DataBaseStorage()


@app.get('/')
def main_route(request: Request, search_text: str = '', department: str = '', organization: int = '', page: int = 0):
    return templates.TemplateResponse('mainpage.html', {
        'request': request,
        'items': phonebook_data.search(search_text, department, organization, page=page),
        'page': page,
        'department': department,
        'organization': organization,
        'pages_count': phonebook_data.get_pages_count()
    })


@app.get('/get_organization_tree')
def get_organization_tree():
    return json.dumps(phonebook_data.organization_tree, ensure_ascii=False)


@app.get('/login')
@app.post('/login')
def login_page(
        request: Request,
        username: Annotated[str, Form()] = '',
        password: Annotated[str, Form()] = '',
        token: str | None = Cookie(default=None),
):
    if token:
        return RedirectResponse('/admin')

    if not username or not password:
        return templates.TemplateResponse('login.html', {
            'request': request,
        })

    username = 'gsprom\\' + username
    ad_conn = ActiveDirectoryConnection()
    if not ad_conn.authenticate_user(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    if not ad_conn.authorize_user(username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для данного раздела",
        )

    response = RedirectResponse('/admin')
    c = CookieUserName(username)
    response.set_cookie(key=c.key, value=c.value, max_age=c.max_age)
    return response


@app.get('/admin')
@app.post('/admin')
def admin_page(request: Request, token: str | None = Cookie(default=None), employee_id: str = ''):
    if not token:
        return RedirectResponse('/login')

    if not ActiveDirectoryConnection().authorize_user(CookieUserName.verify_token(token)):
        raise HTTPException(
            status_code=status.HTTP_401_FORBIDDEN,
            detail="Токен cookie не верифицирован",
        )

    if employee_id:
        pass

    return templates.TemplateResponse('admin.html', {
        'request': request,
    })


@app.get('/logout')
def logout():
    response = RedirectResponse('/login')
    response.delete_cookie('token')
    return response


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
