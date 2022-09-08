from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse, RedirectResponse, JSONResponse

from crawlers import crawler_by_code, newspapers_by_code
from models import Headline

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def split_headlines_in_categories(headlines: [Headline]) -> [str, [Headline]]:
    from collections import OrderedDict
    categories = list(OrderedDict.fromkeys([h.category for h in headlines]))
    split = []
    for category in categories:
        split.append((category, [h for h in headlines if h.category == category]))
    return split


@app.get("/{newspaper}/{path:path}", response_class=HTMLResponse)
async def article(newspaper: str, path: str, request: Request, json: bool = False):
    crawler = crawler_by_code(newspaper)
    article = crawler.fetch_article(path)

    if json:
        return JSONResponse({
            'article': {
                'title': article.title,
                'summary': article.summary,
                'img': article.img,
                'url': article.url,
                'paragraphs': article.paragraphs,
                'published_on': article.published_on,
                'updated_on': article.updated_on,
                'see_also': article.see_also
            },
            "newspaper": {
                "name": crawler.name(),
                "url": crawler.base_url(),
            },
        })

    return templates.TemplateResponse("article.html", {
        "request": request,
        "article": article,
        "newspaper": {
            "name": crawler.name(),
            "url": crawler.base_url(),
        },
        "newspapers": newspapers_by_code(),
        "selected_newspaper": newspaper,
    })


@app.get("/{newspaper}", response_class=HTMLResponse, name="newspaper")
async def headlines(newspaper: str, request: Request, json: bool = False):
    crawler = crawler_by_code(newspaper)
    headlines = crawler.fetch_headlines()
    headlines_in_categories = split_headlines_in_categories(headlines)

    if json:
        return JSONResponse({
            'headlines': [{
                'title': h.title,
                'category': h.category,
                'url': h.url,
                'internal_url': h.internal_url,
                'paywall': h.paywall,
            } for h in headlines],
            'headlines_in_categories': [{
                'category': category,
                'headlines': [{
                    'title': h.title,
                    'url': h.url,
                    'internal_url': h.internal_url,
                    'paywall': h.paywall,
                } for h in category_headlines],
            } for (category, category_headlines) in headlines_in_categories],
            "newspaper": {
                "name": crawler.name(),
                "url": crawler.base_url(),
            },
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "headlines_in_categories": headlines_in_categories,
        "newspaper": {
            "name": crawler.name(),
            "url": crawler.base_url(),
        },
        "newspapers": newspapers_by_code(),
        "selected_newspaper": newspaper,
    })


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/")
async def root(request: Request):
    url = str(request.base_url) + "lesoir"
    response = RedirectResponse(url=url)
    return response
