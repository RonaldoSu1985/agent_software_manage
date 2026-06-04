import asyncio
import aiomysql

async def test_connection():
    try:
        conn = await aiomysql.connect(
            host='192.168.0.118', 
            port=3306, 
            user='agm', 
            password='aa111111', 
            db='agent_management'
        )
        print('Connected successfully')
        conn.close()
    except Exception as e:
        print(f'Connection failed: {e}')

asyncio.run(test_connection())