# Publishing on GitHub

## Browser method

1. Create a GitHub account.
2. Select **New repository**.
3. Name it `shared-evidence-exchange`.
4. Choose **Public** or **Private**.
5. Do not initialize with another README, license, or `.gitignore`.
6. Create the repository.
7. Choose **uploading an existing file**.
8. Extract the downloaded ZIP.
9. Drag the repository contents into GitHub.
10. Commit the upload.

## Command-line method

```bash
cd shared-evidence-exchange
git init
git add .
git commit -m "Initial SEEP starter kit"
git branch -M main
git remote add origin https://github.com/Ctrl-Alt-Karma/shared-evidence-exchange.git
git push -u origin main
```

## Before publishing

- Replace `Ctrl-Alt-Karma` in `README.md` and `pyproject.toml`.
- Confirm the copyright line in `LICENSE`.
- Verify that no real project documents, emails, names, or credentials are included.
- Enable private vulnerability reporting.
