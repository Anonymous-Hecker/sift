Yo people ypur days of Storage pain are over 
# INTRODUCING
# SIFT

A Windows app that removes file-management stress:

1. Renames generic files (image (14).png) based on what is inside them
2. Finds big, rarely used files and moves them to another drive, with your approval
3. Sorts new downloads and keeps a journal so every action can be undone

Status: work in progress (M1 done: drive scanner).

## Run it

    py -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python -m sift scan "C:\Users\YOUR-NAME\Downloads"