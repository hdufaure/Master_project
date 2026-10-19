# Pushing this to GitHub

The repository is already initialised with two commits. Only the remote is missing.

1. Create an **empty** repository on github.com named `ai-inference-energy`
   (no README, no .gitignore, no licence — the files are already here).

2. From inside this folder:

```bash
git remote add origin https://github.com/hdufaure/ai-inference-energy.git
git branch -M main
git push -u origin main
```

If you use SSH instead:
`git remote add origin git@github.com:hdufaure/ai-inference-energy.git`

## Before making it public

Check one thing: `data/specialisation_runs.csv` contains a contact record used
by the extraction task — Claire Vasseur, claire.vasseur@groupe-nord.fr,
01 44 72 09 31. If that was invented for the task, nothing to do. If it came
from a real contact, do not publish it: keep the repository private, or replace
the record and re-run the campaign.

Everything else in here has been checked: no credentials, no absolute paths from
the author's machine, no employer-internal material. The thesis document and the
practitioner interview are deliberately absent.
