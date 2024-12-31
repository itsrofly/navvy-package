from navvy import Navvy

navvy = Navvy("./snake_game")

chunks = navvy.send_message("Create a snake game!")

for chunk in chunks:
    print(chunk, end="", flush=True)
