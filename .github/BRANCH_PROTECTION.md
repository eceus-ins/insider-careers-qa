# Branch Protection & Required Status Checks

After pushing this workflow to GitHub, enable branch protection on `main` so that
the UI tests become a **required check** before merging pull requests.

## Steps

1. Go to **Settings → Branches** in the GitHub repo.
2. Click **Add branch protection rule** → Branch name pattern: `main`.
3. Enable:
   - [x] Require status checks to pass before merging
   - [x] Require branches to be up to date before merging
4. In the **Status checks that are required** search box, add:
   - `Selenium UI Tests (insider_automation_tests)`
   - `Selenium UI Tests (insider_career_tests)`
5. Enable:
   - [x] Require a pull request before merging
   - [x] Do not allow bypassing the above settings
6. Click **Save changes**.

Once saved, every PR to `main` must have green UI tests before it can be merged.
