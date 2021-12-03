# Questionably Usable Image Transporter (Q.U.I.T)

## What?
Use it in conjunction with [HTTP Shortcuts](https://http-shortcuts.rmy.ch/) to share files from your handheld device of choice to be identified, remembered, and stored on a server of your choice.

## Why?
I was tired of downloading pics of anime chicks onto my phone, then having to transfer them over [SFTP](https://www.ssh.com/academy/ssh/sftp), which is **not** fast, to my home media server and manually sort all of it into SFW and NSFW categories. The [Decision Fatigue](https://en.wikipedia.org/wiki/Decision_fatigue) is real, *you know?* 

## How?
1. Clone the repo
2. Create virtual env : `python3 -m venv en`
3. Switch to env : `source env/bin/activate`
4. Install packages : `pip install -r requirements.txt`
5. Open interactive interpreter : `python`
6. Do not freak out as it downloads ~80MB of stuff to somewhere in your user directory.
7. Import genDB : `from app import genDB`
8. Generate Database : `genDB()`
9. Exit the interpreter : `exit()`
10. Run the server : `flask run --port 6969 --host 0.0.0.0`
11. Send images as form-data with name `image` to `http://serveraddress:6969`. More info ahead.

## Where?
- All files are first stored in `TEMP`.
- Those identified as SFW are stored in `SAFE`
- Those identified as NSFW are stored in `UNSAFE`
- The ones that confuse the computer are stored in `FUZZY`, you have to sort them manually.

## Who?
- SFW/NSFW identification powered by [NudeNet](https://github.com/notAI-tech/NudeNet)
- Dupe prevention and image fingerprinting by [ImageHash](https://github.com/JohannesBuchner/imagehash/)


## HTTP Shortcuts
Import this curl command as a shortcut : `curl http://serveraddress:6969 -X POST -m 10000 -F image=@file -F text=junk`

---

*the things I do for thicc anime thighs...*