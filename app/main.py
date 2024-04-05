import json
from typing import Annotated
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, HTTPException, status, Form, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sql_server_connector import DataBaseStorage, SqlServerConnector
from authentication import ActiveDirectoryConnection, CookieUserName


app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

start_time = datetime.now()
phonebook_data = DataBaseStorage()
print(datetime.now() - start_time)


@app.get('/')
def main_route(request: Request, search_text: str = '', department: str | None = None, organization: int | None = None, page: int = 0):
    for i in phonebook_data.search(search_text, department, organization, page=page):
        print(i)
    return templates.TemplateResponse('mainpage.html', {
        'request': request,
        'items': phonebook_data.search(search_text, department, organization, page=page),
        'page': page,
        'department': department,
        'organization': organization,
        'pages_count': phonebook_data.get_pages_count(),
        'search_text': search_text,
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

    user_info = ad_conn.authorize_user(username)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для данного раздела",
        )

    response = RedirectResponse(f'/admin')
    c = CookieUserName(username)
    response.set_cookie(key=c.key, value=c.value, max_age=c.max_age)
    return response


@app.get('/admin')
@app.post('/admin')
def admin_page(
        request: Request,
        token: str | None = Cookie(default=None),
        employee_id: str | None = None,
        confirmation_text: bool = False,
        HidePhotoID: str | None = None,
):
    if not token:
        return RedirectResponse('/login')

    user_info = ActiveDirectoryConnection().authorize_user(CookieUserName.verify_token(token))
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Токен cookie не верифицирован",
        )

    employee_info = None
    if employee_id:
        employee_info = list(filter(lambda employee: employee['ID'] == employee_id, phonebook_data.employees))
        if employee_info:
            employee_info = employee_info[0]

    return templates.TemplateResponse(f'{user_info["group"]}.html', {
        'request': request,
        'employee_id': employee_id,
        'employee_info': employee_info,
        'user_name': user_info['login'],
        'confirmation_text': confirmation_text,
    })


@app.get('/change_data')
@app.post('/change_data')
async def change_data(
        request: Request,
        token: str | None = Cookie(default=None),
):
    if not token:
        return RedirectResponse('/login')

    post_data = await request.form()
    post_data = dict(post_data)

    token_data = CookieUserName.verify_token(token)
    user_info = ActiveDirectoryConnection().authorize_user(token_data)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_FORBIDDEN,
            detail="Токен cookie не верифицирован",
        )
    '''
    Добавить проверку на наличие прав для изменения определенных полей
    '''
    SqlServerConnector().update_data(post_data)

    response = RedirectResponse(f"/{user_info['group']}?employee_id={post_data['ID']}&confirmation_text=True")
    c = CookieUserName(token_data)
    response.set_cookie(key=c.key, value=c.value, max_age=c.max_age)
    return response


@app.get('/logout')
def logout():
    response = RedirectResponse('/')
    response.delete_cookie('token')
    return response


if __name__ == '__main__':
    uvicorn.run(app, host='172.16.153.102', port=8000)
