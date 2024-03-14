import json

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sql_server_connector import DataBaseStorage


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
        'page_list': phonebook_data.get_pages_count()
    })


@app.get('/get_organization_tree')
def get_organization_tree():
    return json.dumps(phonebook_data.organization_tree, ensure_ascii=False)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
