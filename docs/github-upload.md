# GitHub Upload Guide

## Recommended repository name

`edward-smith-qa-ai-portfolio`

## Upload through the GitHub website

1. Create a new public repository with the recommended name.
2. Keep **Add a README file** turned off because this folder already includes one.
3. Upload the contents of this folder, including the `.github` folder if one is added later.
4. Replace the GitHub, LinkedIn, and professional-email placeholders in `README.md`.
5. Add screenshots, live-demo links, and source-code links only after checking that they do not expose credentials or private client information.

## Upload with Git

From inside this folder:

```bash
git init
git add .
git commit -m "Create QA and AI software engineering portfolio"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/edward-smith-qa-ai-portfolio.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Before sharing the link

- Replace all placeholders.
- Confirm every project description is accurate.
- Add screenshots or short GIFs where available.
- Add a live demo or source link for public projects.
- Remove API keys, tokens, private customer data, and unpublished client details.
- Pin the repository on your GitHub profile.

