# Pushing this to GitHub

The repository is already initialised with two commits. Only the remote is missing.

The remote is already configured and the branch is already `main`. From inside
this folder, one command:

```bash
git push -u origin main
```

If you would rather use SSH:

```bash
git remote set-url origin git@github.com:hdufaure/master_project.git
git push -u origin main
```

## Before making it public

Check one thing: `data/specialisation_runs.csv` contains a contact record used
by the extraction task — Claire Vasseur, claire.vasseur@groupe-nord.fr,
01 44 72 09 31. If that was invented for the task, nothing to do. If it came
from a real contact, do not publish it: keep the repository private, or replace
the record and re-run the campaign.

Everything else in here has been checked: no credentials, no absolute paths from
the author's machine, no employer-internal material. The thesis document and the
practitioner interview are deliberately absent.
