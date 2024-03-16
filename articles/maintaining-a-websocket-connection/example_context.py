
# with context manager

with open("dune_quote.txt", "r") as file:
    for line in file:
        print(line.strip())

# without context manager

file = open("dune_quote.txt", "r")
try:
    for line in file:
        print(line.strip())
finally:
    file.close()
