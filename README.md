# Legislative Red Team

A tool that reads a bill or a law and shows where its words fall short of what was promised.

This repository holds the demonstration site. It includes four measures that have already been analyzed:

1. Epstein Files Transparency Act (Public Law 119-38)
2. Surveillance Accountability Act (H.R. 8470)
3. Green New Deal resolution (H.Res. 109, 116th Congress)
4. GRANITE Act (H.R. 10174), on foreign censorship judgments

## What the site shows

For each measure:

1. **Step by step:** one problem at a time, with the page moving to the exact words each problem is about.
2. **One-page summary:** what the measure is, whether it does what it says, its biggest problems, and conflicts of interest.
3. **Full analysis:** every problem in the wording, what is missing, conflicts of interest, what people have said (with sources), and the bigger picture.
4. **Amendments (professional view):** choose drafted amendments and produce a new bill or a marked-up rewrite.

Every line is available in plain language, written for a seventh-grade reading level, and in a professional version.

## How each analysis was made

Each analysis combines two reviews of the same text:

1. **The method.** The tool's step-by-step review, which works from a library of known weaknesses in legislation.
2. **A plain review.** A separate, plain request to the same model, with no library: "What loopholes, red flags, conflicts of interest, missing context, or gaps exist in this legislation, if any:" followed by the text.

Every point from the plain review was checked against the measure's text and against primary sources such as statutes and court rulings. A point was added unless the text or a primary source showed it was wrong. A point that could not be checked against a primary source is shown at low confidence and says so.

## What works on this site, and what does not

1. The four example measures, the guided tour and the knowledge base work fully.
2. Analyzing a new measure does not work on this site. That step needs an analysis service and web research, which a static page cannot provide. On this site the upload form only classifies the text and marks phrases that match known patterns, and labels the result as unreviewed.

## Publishing with GitHub Pages

1. Put the contents of this folder at the top level of a repository, so that `index.html` is in the root.
2. In the repository, open Settings, then Pages.
3. Under Build and deployment, set Source to Deploy from a branch.
4. Choose the `main` branch and the `/ (root)` folder, then save.
5. After a minute or two the site is live at `https://<your-username>.github.io/<repository-name>/`.

## Folder layout

| Path | What it is |
| --- | --- |
| `index.html` | The whole site in one file. This is what GitHub Pages serves. |
| `docs/style-guide.md` | The writing rules every line follows. |
| `docs/conflict-of-interest-review.md` | The conflict of interest method and its types. |
| `src/template.html` | The page's layout, styles and code. |
| `src/build.py` | Runs the style check, then combines the template with the data and writes `index.html`. |
| `src/check_style.py` | Checks every stored line against the style guide. |
| `src/data/measures/` | One file per measure: its text, the professional analysis and the plain-language analysis. |
| `src/data/knowledge-base.json` | The library of weakness patterns, each with what to check and a standard fix. |
| `src/data/rules.json` | Follow-up questions for each kind of weakness, the source index and official drafting standards. |
| `src/data/conflict-types.json` | The conflict of interest method and its types. |
| `src/data/style-guide.json` | The style guide, in the form the page and the checker read. |

## Rebuilding the site

Requires Python 3.9 or later.

```
cd src
python3 build.py
```

The build first checks every stored line against the style guide. If any line fails, it lists the failures and stops. Otherwise it rewrites `index.html`.

## Limits to know about

1. The analyses describe what the wording allows. They take no position on the policy.
2. Legal readings have not been reviewed by outside counsel.
3. The drafted amendments are starting drafts. Each one cites the drafting rule it relies on where one applies, but none has been checked by House or Senate legislative counsel.
4. Conflicts of interest are reported as the cited sources state them. Nothing here says any person acted wrongly.
5. Some patterns in the knowledge base are marked "proposed". They come from research and have not yet been tied to a documented case.
