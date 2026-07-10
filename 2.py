from fastapi import FastAPI,Path, Query,HTTPException,Depends
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse,FileResponse

app = FastAPI()

 #中间件1
@app.middleware("http")
async def middleware1(request,call_next):
    print("start")
    response = await call_next(request)
    print("end")
    return response
#中间件2 
@app.middleware("http")
async def middleware2(request,call_next):
    print("start")
    response = await call_next(request)
    print("end")
    return response     
@app.get("/user/hello")
async def get_userhello():
    return {"msg":"我正在学习fastapi"}
@app.get("/user/{id}/{name}")
async def get_id(id:int,name:str):
    return{"id":id,"name":name}
@app.get("/news/id/{id}")
async def news_id(id : int = Path(...,gt=0,le=100)):
    return{"news id":id}
@app.get("/news/name/{name}")
async def news_name(name : str = Path(...,max_length=10,min_length=2)):
    return{"news name":name}
@app.get("/book/category")
async def get_book(booktype : str = Query("python开发",max_length=255,min_length=5),price : int = Query(...,ge=50,le=100)):
    return{"booktype":booktype,"price":price}
class Bookinformation(BaseModel):
    name : str = Field(...,max_length=20,min_length=2)
    author : str =Field(...,max_length=10,min_length=2)
    publisher : str = Field("黑马出版社")
    price : int = Field(...,gt=0)
@app.post("/book/information")
async def information(information:Bookinformation):
    return information
@app.get("/html",response_class=HTMLResponse)
async def get_html():
    return "<h1>田曦薇</h1>"
@app.get("/file")
async def get_file():
    path = "./file/1.jpeg"
    return FileResponse(path)
@app.get("/bookfind/{name}",response_model=Bookinformation)
async def bookfind(name:str):
    return{
        "name" : name,
        "author" :"作者",
        "publisher":"出版社",
        "price" : 99
    }
#抛出异常
@app.get("/booklist/{name}")
async def get_booklist(name:str):
    name_list = ["li","ai","qi"]
    if name not in name_list:
        raise HTTPException(status_code=404,detail="您输入的书名不存在")
    return {"name":name}
#依赖项
async def common_parameters(skip:int = Query(0,ge=0),limit:int = Query(10,le=60)):
    return {"skip":skip,"limit":limit}
#注入依赖
@app.get("/news/news1")
async def new1(commons=Depends(common_parameters)):
    return commons
