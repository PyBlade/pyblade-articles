import random
import time

async def print_duote_quote():
    async with aiofiles.open("dune_quote.txt", "r") as file:
        content = await file.read()
        for line in content.split("\n"):
            print(line.strip())

def simple_generator():
    yield 1
    yield 2
    yield 3

"uncomment to run example"
# gen = simple_generator()
# while True:
#     print(next(gen))


def random_number_printer():
    print(random.randint(0, 10))

def function_generator():
    while True:
        yield random_number_printer

"uncomment to run example"
# gen = function_generator()
# while True:
#     show_me_random_int = next(gen)
#     show_me_random_int()
#     time.sleep(1)