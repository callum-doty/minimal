# Updated Minimal Render Deployment Instructions

Based on the issues encountered, here are updated deployment instructions:

## Preparation

1. Make sure you're in the project root directory (not inside minimal_render_deploy):

   ```
   cd /Users/callumd/Desktop/project_catalog-1
   ```

2. Run the preparation script:
   ```
   ./prepare_minimal_deploy.sh
   ```

## Git Repository Setup

There are two options for setting up the Git repository:

### Option 1: Create a new repository from scratch

1. Create a new empty repository on GitHub/GitLab/Bitbucket (do not initialize it with README or .gitignore)

2. Navigate to the minimal_render_deploy directory:

   ```
   cd minimal_render_deploy
   ```

3. If the remote origin already exists, remove it:

   ```
   git remote remove origin
   ```

4. Add your new repository as the remote origin:

   ```
   git remote add origin <your-new-repo-url>
   ```

5. Push to the new repository:
   ```
   git push -u origin main
   ```

### Option 2: Use a branch in an existing repository

If you want to use an existing repository but create a new branch for the minimal deployment:

1. Navigate to the minimal_render_deploy directory:

   ```
   cd minimal_render_deploy
   ```

2. Create a new branch:

   ```
   git checkout -b minimal-render
   ```

3. If you get conflicts when pushing, force push (only if you're sure this is a new branch):
   ```
   git push -u origin minimal-render --force
   ```

## Deploying to Render

1. Log in to your Render account

2. Click "New" and select "Blueprint"

3. Connect your Git repository and select the appropriate branch:

   - If using Option 1: select the main branch
   - If using Option 2: select the minimal-render branch

4. Render will automatically detect the render.yaml file and configure the service

5. Click "Apply" to start the deployment

## After Deployment

1. Once deployed, you can verify the application is running by visiting the URL provided by Render

2. In the Render dashboard, navigate to your web service

3. Click on the "Shell" tab to access SSH

4. You should now have SSH access to your application and can apply your full application using:
   ```
   appuser@project-catalog-2-0-shell:/app$
   ```

## Troubleshooting

- If you see "cd: no such file or directory: minimal_render_deploy", you may already be inside the directory. Check your current location with `pwd`.

- If you see "error: remote origin already exists", use `git remote remove origin` before adding a new one.

- If you see "Updates were rejected because the remote contains work that you do not have locally", either:
  - Pull the changes first: `git pull origin main --rebase`
  - Or use a different branch name and force push: `git checkout -b minimal-render && git push -u origin minimal-render --force`
