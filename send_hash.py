import asyncio, json
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def main():
    t=StreamableHttpTransport('https://further-favourite-theft-stars.trycloudflare.com/mcp')
    async with Client(t) as c:
        print(await c.call_tool('submit_audit', {'payload': {'sender':'thief','records':[],'result_claim':'series_consensus','consensus_sha':'4efbc1400e81f7fce0aa69da228f1382aad114958f58b46fc3e2bf13e44be131'}}))

asyncio.run(main())
