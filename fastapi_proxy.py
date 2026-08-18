import uvicorn
from fastapi import FastAPI, Request, Response
import httpx
from fastapi.responses import StreamingResponse

app = FastAPI()
client = httpx.AsyncClient(base_url="http://127.0.0.1:8001")

@app.head("/mcp")
async def head_mcp():
    return Response(status_code=200)

@app.get("/mcp")
async def get_mcp(request: Request):
    req = client.build_request("GET", "/sse", headers=request.headers)
    resp = await client.send(req, stream=True)
    return StreamingResponse(resp.aiter_raw(), status_code=resp.status_code, headers=dict(resp.headers))

@app.post("/messages")
async def post_messages(request: Request):
    body = await request.body()
    req = client.build_request("POST", "/messages", content=body, headers=request.headers)
    resp = await client.send(req)
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8011)
