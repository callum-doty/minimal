# Minimal Render Deployment

This guide explains how to deploy a minimal version of the application to Render to enable SSH access.

## Files

- `direct.py`: A minimal Flask application that binds to 0.0.0.0 and provides a health check endpoint
- `direct-start.sh`: A script to start the minimal application
- `minimal.Dockerfile`: A simplified Dockerfile for the minimal application
- `minimal_requirements.txt`: A minimal set of dependencies
- `minimal_render.yaml`: A simplified Render configuration

## Deployment Steps

1. **Create a new Git repository**

   Create a new Git repository and push these files to it:

   - direct.py
   - direct-start.sh
   - minimal.Dockerfile
   - minimal_requirements.txt
   - minimal_render.yaml (rename to render.yaml when pushing)

2. **Deploy to Render**

   a. Log in to your Render account
   b. Click "New" and select "Blueprint"
   c. Connect your Git repository
   d. Render will automatically detect the render.yaml file and configure the service
   e. Click "Apply" to start the deployment

3. **Verify Deployment**

   Once deployed, you can verify the application is running by visiting the URL provided by Render. You should see a JSON response indicating the service is online.

4. **Enable SSH Access**

   a. In the Render dashboard, navigate to your web service
   b. Click on the "Shell" tab
   c. You should now have SSH access to your application

5. **Apply Your Application**

   Once you have SSH access, you can apply your application using:

   ```
   appuser@project-catalog-2-0-shell:/app$
   ```

## Troubleshooting

- If the deployment fails, check the logs in the Render dashboard for error messages
- Ensure the health check endpoint is working correctly
- Verify that the application is binding to the correct port (the one provided by Render)
