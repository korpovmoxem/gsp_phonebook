import os
from datetime import datetime, timedelta
import json

import uvicorn
from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
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
        'organization_tree': phonebook_data.organization_tree,
        'page': page,
        'department': department,
        'organization': organization,
    })


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)


