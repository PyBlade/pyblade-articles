# Maintaining a Websocket Connection

Motivation: I know how to create websocket connection, send and receive messages but how the hell do I maintain it!?!

When I first tackled this problem I would write all sorts of try except blocks, fighting tooth and nail to re-connect. Later I discovered a different approach that I want to share with you. It simply boils down to:

> "*Websocket dropped, forget it and generate a new one*"

This may sound too simplistic but bear with me! Now I could immediately be pretentious and say that we are going to create an *asynchronous context generator* as if I was some stack overflow logic artisan. Sounds comlicated? It's not, it's just designed to sound like it!

I'll first cover some basic examples of the topics you need to know and then bring it all together. Or you can scroll to the bottom and see the final example.

## Generator

A generator in Python is a function that returns an iterator. It generates values on the fly using the `yield` keyword. A simple example that throws an exception:

```python
def simple_generator():
    yield 1
    yield 2
    yield 3

gen = simple_generator()
while True:
    print(next(gen))
```

Eventually:

```
Traceback (most recent call last):
    print(next(gen))
StopIteration
```

Because the iterator has been exhausted, it has nothing left to return when asked to do so. Let's now code an iterator that is never exhausted that also returns a simple function.

```python
import random
import time

def random_number_printer():
    print(random.randint(0, 10))

def function_generator():
    while True:
        yield random_number_printer


gen = function_generator()

while True:
    show_me_random_int = next(gen)
    show_me_random_int()
    time.sleep(1)
```
### Takeaway no. 1

The main point to take away from here is that we can use `while True` inside a generator.

## Context


A defined and enforced convention of entering and exiting that particular indented code block.

A context manager is the object that dictates what should happen upon entering and exiting the context. `with open` is a built-in context manager. In fact any context that your code enters into will start with `with`. In natural language you can think of it as *within this context do this*

```python
# see repo for accompanying file or add your own file with some text 
with open("dune_quote.txt", "r") as file:
    for line in file:
        print(line.strip())
```

```
It is so shocking to find out how many people do not believe that they can learn, 
and how many more believe learning to be difficult.
```

We can still access the file without using open as a context manager but it results in more code and there is also the risk we don't close the file which can lead to all sorts of trouble. `with open` we can basically enter the file, do our business and get out, and personally I think it reads better than:

```python
file = open("dune_quote.txt", "r")
try:
    for line in file:
        print(line.strip())
finally:
    file.close()
```

The `try`, `finally` is not necassary here but it is good practice to ensure the file was properly closed. I'll leave it to the reader to learn what could happen if we left the file open. Using the `with` to open the context we get the same guarantee as finally that the file will be closed, because we have to exit the context to end the program, even if the exit was caused by an exception.

Variables that were created within the context are not lost when exiting it.

### Takeaway no. 2

A context generator defines how we enter and exit a block of code using the `with` and `as` keywords. We do not lose data when we exit the context.

## Async

Short for asynchronous which allows for concurrency, i.e. do many seperate things at the same time which is very useful for operations where we are waiting for things rather than computing them.

* Putting `async def` declares that this is an asynchronous function and we can use the associated keywords and perform tasks concurrently (do many things at the same time)
* When we call an async function it creates a coroutine which does not automatically start executing, it needs to be scheduled to run on an event loop which is handled by `asyncio.run`.
* `async def` allows us to create an asynchronous context which is very similar to the file example earlier:


```python
import asyncio
import aiofiles

async def print_duote_quote():
    async with aiofiles.open("dune_quote.txt", "r") as file:
        content = await file.read()
        for line in content.split("\n"):
            print(line.strip())

asyncio.run(print_duote_quote())
```

The `await` keyword is telling Python *"this might take a while, feel free to do other things while you wait for it to return"*. When you first start using these keywords it's common to forgot them. The Exception:

```
RuntimeWarning: coroutine ... was never awaited
```

Is a dead give away that you've forgotten `await` at the given line in the exception message.

I'm only covering basic async topics that we need for this article. To fully learn and master can be a challenge.

### Takeaway

Going full async is hard, the basics is not.

## Websockets

The websockets library creates a connection within an asynchronous context manager. Similar order of operations as our async file context manager.

1. Open a websocket connection.
2. Do our business with the connection
3. Close the connection

```python
import asyncio
import websockets
import json

URL = "wss://www.deribit.com/ws/api/v2"

async def print_btc_ticker():
    async with websockets.connect(URL) as websocket:
        msg = {
            "jsonrpc": "2.0",
            "method": "public/ticker",
            "params": {
                "instrument_name": "BTC-PERPETUAL"
            }
        }
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        print(response)

asyncio.run(print_btc_ticker())
```

1. Open the websocket connection.
2. Request and print some exchange information
3. Close the websocket connection.

### Takeaway

Conceptually entering and exiting the context provided by websockets is the same as opening and closing the file.

## Generate Websocket Connection

So we know:
 * How to construct a generator
 * What a context manager is and what it provides
 * Basic async keywords
 * Creating a websocket connection context

Now let's build a generator which always yields a websocket connection, sounds complicated. It's not:

```python
import websockets

URL = "wss://www.deribit.com/ws/api/v2"

async def websocket_generator():
    while True:
        async with websockets.connect() as websocket:
            yield websocket
```

And to use it in the previous `print_btc_ticker` example, we simply change the context manager to an iterator remembering the `async` keyword in the iteration:

```python
async def print_btc_ticker():
    async for websocket in websocket_generator():
        msg = {
            "jsonrpc": "2.0",
            "method": "public/ticker",
            "params": {
                "instrument_name": "BTC-PERPETUAL"
            }
        }
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        print(response)
        break

asyncio.run(print_btc_ticker())
```
Remember we are now iterating over a generator that utilises `while True`, hence the `break`

We've covered some hopefully easily digested topics and created an asynchronous context generator. Now let's spruce it up with some exception handling and logging to maintain the connection. I will also use a different endpoint to stream prices rather than a simple information request.

```python
async def websocket_generator(retry_seconds=5):
    """Generates a new websocket connection. Retries on failure."""
    while True:
        try:
            async with websockets.connect("wss://www.deribit.com/ws/api/v2") as websocket:
                yield websocket
        except Exception as e:
            logging.error(f"Websocket connection failed: {e}")
            asyncio.sleep(retry_seconds)
            continue
```

You could argue that we should use a narrower exception from the websockets library but in this example our priority is to keep the connection and by using logging we are not failing silently, unless nobody checks the logs...

We improve the `print_btc_ticker` in a similar way.

```python
async def print_btc_ticker():
    """Prints BTC ticker data from Deribit."""
    async for websocket in websocket_generator():
        try:
            # Subscribe to BTC-PERPETUAL ticker data
            msg = {
                "jsonrpc": "2.0",
                "method": "public/subscribe",
                "params": {
                    "channels": ["ticker.BTC-PERPETUAL.100ms"]
                }
            }
            await websocket.send(json.dumps(msg))
            # Continue to listen to incoming messages and print them
            while websocket.open:
                response = await websocket.recv()
                print(response)
        # if anything goes wrong, log the error and continue
        except Exception as e:
            logging.error(f"Error in print_btc_ticker: {e}")
            continue
            # no sleep required here because that's already handled by the generator

asyncio.run(print_btc_ticker())
```

## Summary

Instead of writing overly defensive code to maintain a websocket connection we can instead forget about the connection that failed and create a new one. Because the connection is a context we do not lose data in memory because a context does not constitute it's own name space.

I hope you found this useful! 
