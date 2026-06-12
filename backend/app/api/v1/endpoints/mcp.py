from fastapi import FastAPI, Request, Response
from app.services.mcp_service import mcp, current_user_id
from app.models.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

mcp_app = FastAPI(title="SoftManage MCP Server")

@mcp_app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # 允许健康检查或其他不需要 key 的路径（如果有）
    if request.url.path == "/":
        return await call_next(request)
        
    # 获取 MCP Key
    key = request.query_params.get("key")
    if not key:
        return Response("Missing MCP Key. Please provide ?key=YOUR_KEY in the URL.", status_code=401)
    
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.mcp_key == key)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return Response("Invalid MCP Key.", status_code=401)
        
        # 设置当前操作用户的上下文，供 MCP tools 使用
        token = current_user_id.set(user.id)
        try:
            response = await call_next(request)
            return response
        finally:
            current_user_id.reset(token)

# 挂载 MCP SSE 传输
# 这将返回一个 Starlette/FastAPI 应用，包含 /sse 和 /messages 接口
mcp_sse_app = mcp.sse_app()
mcp_app.mount("/", mcp_sse_app)
