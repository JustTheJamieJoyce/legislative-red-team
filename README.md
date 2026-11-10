# Legislative Red Team

A tool that reads a bill or a law and shows where its words fall short of what was promised.

This repository holds the demonstration site. It includes three measures that have already been analyzed:

- Epstein Files Transparency Act (Public Law 119-38)
- Surveillance Accountability Act (H.R. 8470)
- Green New Deal resolution (H.Res. 109, 116th Congress)

## What the site shows

For each measure:

- **Step by step**: one problem at a time, with the page moving to the exact words each problem is about.
- **One-page summary**: what the measure is, whether it does what it says, its biggest problems, and conflicts of interest.
- **Full analysis**: every problem in the wording, what is missing, conflicts of interest, what people have said (with sources), and the bigger picture.
- **Amendments** (professional view): choose drafted amendments and produce a new bill or a marked-up rewrite.

Every line is available in plain language, written for a seventh-grade reading level, and in a professional version.

## What works on this site, and what does not

- The three example measures, the guided tour and the knowledge base work fully.
- **Analyzing a new measure does not work on this site.** That step needs an AI service and web research, which a static page cannot provide. On this site the upload form only classifies the text and marks phrases that match the pattern library, and labels the result as unreviewed.

## Publishing with GitHub Pages

1. Put the contents of this folder at the top level of a repository, so that `index.html` is in the root.
2. In the repository, open **Settings**, then **Pages**.
3. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
4. Choose the `main` branch and the `/ (root)` folder, then save.
5. After a minute or two the site is live at `https://<your-username>.github.io/<repository-name>/`.

The file `.nojekyll` tells GitHub to serve the files as they are.

## Folder layout

| Path | What it is |
|---|---|
| `index.html` | The whole site in one file. This is what GitHub Pages serves. |
| `docs/style-guide.md` | The writing rules every line follows. |
| `docs/conflict-of-interest-review.md` | The conflict of interest method and its types. |
| `docs/drafting-critique-sources.md` | Research on sources that critique legislation and on official drafting standards. |
| `src/template.html` | The page's layout, styles and code. |
| `src/build.py` | Combines the template with the data and writes `index.html`. |
| `src/analysis/` | The stored analysis of each measure. |
| `src/texts/` | The text of each measure. |
| `src/style/` | The style guide, the professional and plain-language wording, and the checker. |
| `src/kb.json`, `src/rules.json`, `src/coi.json` | The pattern library, the follow-up question rules and the conflict types. |

## Rebuilding the site

Requires Python 3.

```
cd src
python3 build.py
```

This checks every stored line against the style guide and rewrites `index.html`. The build prints `STYLE GATE: pass` when every line passes.

## Limits to know about

- The analyses describe what the wording allows. They take no position on the policy.
- Legal readings have not been reviewed by outside counsel.
- The drafted amendments are starting drafts and have not been checked against House or Senate drafting conventions.
- Conflicts of interest are reported as the cited sources state them. Nothing here says any person acted wrongly.
