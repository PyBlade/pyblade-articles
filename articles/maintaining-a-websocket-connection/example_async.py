import asyncio
import aiofiles

async def print_duote_quote():
    async with aiofiles.open("dune_quote.txt", "r") as file:
        content = await file.read()
        for line in content.split("\n"):
            print(line.strip())

if __name__ == "__main__":
    
    asyncio.run(print_duote_quote())
