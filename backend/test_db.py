import asyncio
import aiomysql

async def test_connection():
    try:
        conn = await aiomysql.connect(
            host='192.168.6.10', 
            port=37061, 
            user='product', 
            password='product123', 
            db='agent_management'
        )
        print('Connected successfully')
        await conn.close()
    except Exception as e:
        print(f'Connection failed: {e}')

asyncio.run(test_connection())