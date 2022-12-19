from dataclasses import dataclass
from rich.console import Console
from rich.table import Table

save_filename = "../scores.txt"

@dataclass
class entry:
    score: int
    username: str


entries: list[entry] = []

with open(save_filename, "r") as file:
    lines: list[str] = file.readlines()
    for line in lines:
        if len(line) < 1:
            continue
        line = line.strip()
        split = line.split(":")
        skip = False
        for en in entries:
            if en.username == split[1]: #if matching usernames
                if en.score < int(split[0]): #new score is bigger than current score
                    entries.remove(en)
                else:
                    skip = True
                break
        if skip:
            continue

        new_entry = entry(int(split[0]), split[1])
        entries.append(new_entry)
        
entries.sort(key=lambda x:x.score, reverse=True)

console = Console()

table = Table(show_header=True, header_style="bold magenta")
table.add_column("Rank", style="dim")
table.add_column("Username")
table.add_column("Score")

for idx, en in enumerate(entries):
    rank = idx+1
    table.add_row(str(rank), en.username, str(en.score))

console.print(table)
input()