#!/bin/env python3

__author__ = "Patrick Coffey, 2022"
__license__ = """
Copyright (c) 2022, Patrick Coffey
All rights reserved
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by the Menzies-Ramaciotti Centre.
4. Neither the name of the Menzies-Ramaciotti Centre nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
__doc__ = """
find_mshr.py
============

Recursively searches folders for files starting at `--root` for files that match `--pattern`.

usage: `find_mshr.py <command> <args>`

commands
--------

    search
    ------

        Used for searching for files, this just lists them out, but can be piped to a file
        for use later.

        args
        ----

        --file [-l] (str):  A file containing a list (white space sep) of MSHR
                            ID's to include. eg. 123 124 125 ...
        --root [-r] (str):  [OPTIONAL] where to start recursively searching from (default: ".")

        example
        -------

        # pipes a list of all *.fastq.gz files in any directory below 
        # "/data/x" into a file called "list_of_fastq.txt"

        find_mshr.py search --root "/data/x" --pattern "*.fastq.gz" > list_of_fastq.txt
        # or 
        find_mshr.py search -r "/data/x" -p "*.fastq.gz" > list_of_fastq.txt

    link
    ----

        Used to create a set of soft links into the `--target` folder. This can be either given 
        a `--file` which contains a list of the file paths to link here, or it can be given 
        arguments like the `search` command to preform a search and link in a single action.

        args
        ----

        --file [-l] (str):      A file containing a list (white space sep) of MSHR
                                ID's to include. eg. 123 124 125 ...
        --target [-t] (str):    [OPTIONAL] the folder to link the files to (default: ".")
        --root [-r] (str):      [OPTIONAL] where to start recursively searching from (default: ".")

        example
        -------

        # soft-links mshr files witch matching Id's found in "/data/x" folder into the 
        # "/home/me/x" folder.

        find_mshr.py link --file list_of_mshr_ids.txt --root "/data/x" --target "/home/me/x"
        # or 
        find_mshr.py link -f list_of_mshr_ids.txt -t "/home/me/x"

        # actual command that i used as part of my BPS training program
        find_mshr.py link \\
            --file "/home/pcoffey/projects/bps_project/mshr_lists/all.txt" \\
            --target "/home/pcoffey/projects/bps_project/genomes/all" \\
            --root "/data/melioidosis/genomes/Bpseudomallei/"

    dry-link
    --------

        Same as link, except wont actually create the links, instead it just prints the links it
        would have made. Useful for checking links before actually creating them. Accepts all the 
        same arguments and behaves the same as the `link` command.

Patrick Coffey, 2022
"""

import sys
import re
from typing import Dict, List
from pathlib import Path


def load_from_file(file: Path) -> List[int]:
    if not file.exists():
        exit("file {} doesn't exist!".format(file.as_posix()))
    return [int(x) for x in file.read_text().split()]


def print_search_output(results: List[Path]):
    print("\n".join([x.as_posix() for x in results]))


def extract_mshr_id(
    file: Path,
    mshr_extract_pattern: str = r"(?:[a-zA-Z_\/\\]*)MSHR([0-9]+)(?:[MIXED]?)(?:[\w-]*)_(?:[R]?)([0-9]+)",
) -> str:
    mshr_pattern = re.compile(mshr_extract_pattern)
    match = mshr_pattern.search(Path(file).as_posix())
    if match:
        mshr_id_n = "{}-{}".format(int(match[1]), int(match[2]))
        return mshr_id_n


def filter_for_mshr_id(
    results: List[Path],
    id_list: List[str],
) -> List[Path]:

    ret_list = []
    for file in results:
        mshr_id_n = extract_mshr_id(file)
        if not mshr_id_n:
            continue
        mshr_id = int(mshr_id_n.split("-")[0])
        if mshr_id in id_list:
            ret_list.append(file)
    return ret_list


def solve_duplicates(
    file_paths: List[Path], resolution_policy: str = "newest"
) -> List[Path]:
    file_map: Dict[int, List[Path]] = {}
    for file in file_paths:
        mshr_id = extract_mshr_id(file)
        if not file_map.get(mshr_id):
            file_map[mshr_id] = []
        file_map[mshr_id].append(file)

    ret_list = []
    for mshr_id, file_paths in file_map.items():
        if len(file_paths) > 1:
            if resolution_policy == "newest":
                newest = file_paths[0]
                for file in file_paths:
                    if file.stat().st_ctime > newest.stat().st_ctime:
                        newest = file
                ret_list.append(newest)
        else:
            ret_list.append(file_paths[0])

    return ret_list


def do_search(
    file: Path = None,
    root: Path = ".",
    pattern: str = "*",
    allow_list: List[str] = ["mshr"],
    deny_list: List[str] = ["mixed"],
) -> List[Path]:
    raw_results = [x for x in Path(root).rglob(pattern)]
    if file:
        id_list = load_from_file(Path(file))
        raw_results = filter_for_mshr_id(raw_results, id_list)
    allowed = [
        x for x in raw_results for a in allow_list if a in str(x.as_posix()).lower()
    ]
    denied = [
        x for x in raw_results for d in deny_list if d in str(x.as_posix()).lower()
    ]
    return [a for a in allowed if a not in denied]


def search(
    file: Path = None,
    root: Path = None,
    pattern: str = None,
    allow_list: List[str] = ["mshr"],
    deny_list: List[str] = ["mixed"],
) -> str:
    root = root or "."
    pattern = pattern or "*"
    results = do_search(
        file=file,
        root=root,
        pattern=pattern,
        allow_list=allow_list,
        deny_list=deny_list,
    )
    print_search_output(results)


def link(
    root: Path = None,
    pattern: str = None,
    target: Path = None,
    file: Path = None,
    dry_run: bool = False,
):
    if file is None and target is None:
        exit("Must specify either --file or --root and --pattern arguments!")

    root = root or "."
    pattern = pattern or "*"
    target = target or "."

    file_paths = do_search(file=file, root=root, pattern=pattern)

    file_paths = solve_duplicates(file_paths)

    for source in file_paths:
        this_target = Path(target / source.name)
        if dry_run:
            print("{} -> {}".format(this_target.absolute(), source.absolute()))
            continue
        this_target.absolute().symlink_to(source.absolute())


def dry_link(
    root: Path = None, pattern: str = None, target: Path = None, file: Path = None
):
    link(root=root, pattern=pattern, target=target, file=file, dry_run=True)


def exit(message: str = None):
    if message:
        print(message)
    raise SystemExit(__doc__)


def main():

    root = None
    pattern = None
    target = None
    file = None

    try:
        if sys.argv[1] == "search":
            opts = [opt for opt in sys.argv[2:] if opt.startswith("-")]
            args = [arg for arg in sys.argv[2:] if not arg.startswith("-")]

            if not len(opts) == len(args):
                exit("All arguments require parameters!")

            for idx, opt in enumerate(opts):
                if opt in ("-r", "--root"):
                    root = Path(args[idx])
                elif opt in ("-p", "--pattern"):
                    pattern = args[idx]
                elif opt in ("-f", "--file"):
                    file = args[idx]

            search(root=root, pattern=pattern, file=file)

        elif sys.argv[1] in ("link", "dry-link"):
            opts = [opt for opt in sys.argv[2:] if opt.startswith("-")]
            args = [arg for arg in sys.argv[2:] if not arg.startswith("-")]

            if not len(opts) == len(args):
                exit("All arguments require parameters!")

            for idx, opt in enumerate(opts):
                if opt in ("-r", "--root"):
                    root = Path(args[idx])
                elif opt in ("-p", "--pattern"):
                    pattern = args[idx]
                elif opt in ("-t", "--target"):
                    target = Path(args[idx])
                elif opt in ("-f", "--file"):
                    file = Path(args[idx])

            link(
                root=root,
                pattern=pattern,
                target=target,
                file=file,
                dry_run=True if sys.argv[1] == "dry-link" else False,
            )

        else:
            exit("Must call a sub command! (search, link, dry-link)")
    except Exception as e:
        raise e
        exit(e)


if __name__ == "__main__":

    main()
