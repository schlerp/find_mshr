# find_mshr.py

Recursively searches folders for files starting at `--root` for files that match `--pattern`.

usage: `find_mshr.py <command> <args>`

## commands

### search

Used for searching for files, this just lists them out, but can be piped to a file
for use later.

#### args

    --file [-l] (str):  A file containing a list (white space sep) of MSHR ID's to include. 
                        eg. 123 124 125 ...
    --root [-r] (str):  [OPTIONAL] where to start recursively searching from (default: ".")

#### example

```bash
# pipes a list of all *.fastq.gz files in any directory below 
# "/data/x" into a file called "list_of_fastq.txt"

find_mshr.py search --root "/data/x" --file "list_of_mshr_ids.txt"
# or 
find_mshr.py search -r "/data/x" -f "list_of_mshr_ids.txt"
```

### link

Used to create a set of soft links into the `--target` folder. This can be either given 
a `--file` which contains a list of the file paths to link here, or it can be given 
arguments like the `search` command to preform a search and link in a single action.

#### args

    --file [-l] (str):      A file containing a list (white space sep) of MSHR ID's to include. 
                            eg. 123 124 125 ...
    --target [-t] (str):    [OPTIONAL] the folder to link the files to (default: ".")
    --root [-r] (str):      [OPTIONAL] where to start recursively searching from (default: ".")

#### example

```bash
# soft-links mshr files witch matching Id's found in "/data/x" folder into the 
# "/home/me/x" folder.

find_mshr.py link --file list_of_mshr_ids.txt --root "/data/x" --target "/home/me/x"
# or 
find_mshr.py link -f list_of_mshr_ids.txt -r "/data/x"  -t "/home/me/x"

# actual command that i used as part of my BPS training program
find_mshr.py link \\
    --file "/home/pcoffey/projects/bps_project/mshr_lists/all.txt" \\
    --target "/home/pcoffey/projects/bps_project/genomes/all" \\
    --root "/data/melioidosis/genomes/Bpseudomallei/"
```

### dry-link

Same as link, except wont actually create the links, instead it just prints the links it
would have made. Useful for checking links before actually creating them. Accepts all the 
same arguments and behaves the same as the `link` command.

## Installing

easiest way would be to just curl it down into your ~/bin folder and call it from there (make sure you `chmod +x find_mshr.py`).

```bash
# can skip if you already have a ~/bin
mkdir -p ~/bin

# change into ~/bin
cd ~/bin

# curl the script down (download it)
curl -o find_mshr.py https://raw.githubusercontent.com/schlerp/find_mshr/main/find_mshr.py

# enable direct execution
chmod +x find_mshr.py
```

## Author

[Patrick Coffey](https://github.com/schlerp), 2022
