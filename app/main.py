import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Request, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Папка внутри контейнера, куда ОС будет монтировать файлы
STORAGE_DIR = "/storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

templates = Jinja2Templates(directory="app/templates")

def get_file_info(filename):
    file_path = os.path.join(STORAGE_DIR, filename)
    stat = os.stat(file_path)
    size_bytes = stat.st_size

    # Переводим байты в читаемый вид
    if size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.2f} КБ"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.2f} МБ"

    return {
        "name": filename,
        "size": size_str,
        "size_raw": size_bytes,
        "time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "time_raw": stat.st_mtime
    }

@app.get("/", response_class=HTMLResponse)
async def list_files(
    request: Request,
    search: str = Query(None),
    sort_by: str = Query("time"),
    order: str = Query("desc")
):
    all_files = os.listdir(STORAGE_DIR)
    file_list = []

    for filename in all_files:
        if filename.startswith('.'):
            continue
        if search and search.lower() not in filename.lower():
            continue
        file_list.append(get_file_info(filename))

    reverse_sort = True if order == "desc" else False
    if sort_by == "name":
        file_list.sort(key=lambda x: x["name"].lower(), reverse=reverse_sort)
    elif sort_by == "size":
        file_list.sort(key=lambda x: x["size_raw"], reverse=reverse_sort)
    else:
        file_list.sort(key=lambda x: x["time_raw"], reverse=reverse_sort)

    return templates.TemplateResponse("index.html", {
        "request": request, "files": file_list, "search": search or "", "sort_by": sort_by, "order": order
    })

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(STORAGE_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return HTMLResponse(content="<script>window.location.href='/';</script>", status_code=200)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    return {"error": "Файл не найден"}
