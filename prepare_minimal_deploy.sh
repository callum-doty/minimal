#!/bin/bash
# Script to prepare files for minimal Render deployment

set -e  # Exit immediately if a command exits with a non-zero status

echo "=== Preparing Minimal Render Deployment ==="

# Check if we're already in the minimal_render_deploy directory
CURRENT_DIR=$(basename $(pwd))
if [ "$CURRENT_DIR" == "minimal_render_deploy" ]; then
    echo "ERROR: You appear to be already inside the minimal_render_deploy directory."
    echo "Please run this script from the project root directory:"
    echo "  cd /Users/callumd/Desktop/project_catalog-1"
    echo "  ./prepare_minimal_deploy.sh"
    exit 1
fi

# Create deployment directory
DEPLOY_DIR="minimal_render_deploy"
if [ -d "$DEPLOY_DIR" ]; then
    echo "WARNING: $DEPLOY_DIR directory already exists."
    read -p "Do you want to remove it and create a fresh deployment? (y/n): " CONFIRM
    if [ "$CONFIRM" == "y" ] || [ "$CONFIRM" == "Y" ]; then
        rm -rf $DEPLOY_DIR
        echo "Removed existing $DEPLOY_DIR directory."
    else
        echo "Aborting. Please remove or rename the existing directory manually if needed."
        exit 1
    fi
fi

mkdir -p $DEPLOY_DIR
echo "Created deployment directory: $DEPLOY_DIR"

# Copy necessary files
cp direct.py $DEPLOY_DIR/
cp direct-start.sh $DEPLOY_DIR/
cp minimal.Dockerfile $DEPLOY_DIR/Dockerfile
cp minimal_requirements.txt $DEPLOY_DIR/requirements.txt
cp minimal_render.yaml $DEPLOY_DIR/render.yaml
cp MINIMAL_DEPLOY.md $DEPLOY_DIR/README.md
cp UPDATED_DEPLOY_INSTRUCTIONS.md $DEPLOY_DIR/

# Update the Dockerfile to use the correct requirements file path
sed -i.bak 's/COPY minimal_requirements.txt \/app\/requirements.txt/COPY requirements.txt \/app\//' $DEPLOY_DIR/Dockerfile
rm $DEPLOY_DIR/Dockerfile.bak

echo "Copied all necessary files to $DEPLOY_DIR"

# Make scripts executable
chmod +x $DEPLOY_DIR/direct-start.sh

echo "Made scripts executable"

# Create a basic .gitignore
cat > $DEPLOY_DIR/.gitignore << EOL
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.DS_Store
EOL

echo "Created .gitignore file"

# Initialize git repository
cd $DEPLOY_DIR
git init
git add .
git commit -m "Initial commit for minimal Render deployment"

echo "Initialized Git repository"
echo ""
echo "=== Deployment Preparation Complete ==="
echo ""
echo "Next steps:"
echo ""
echo "Option 1: Create a new repository from scratch"
echo "----------------------------------------"
echo "1. Create a new empty repository on GitHub/GitLab/Bitbucket"
echo "2. Set up the remote (from the $DEPLOY_DIR directory):"
echo "   # If remote already exists:"
echo "   git remote remove origin"
echo "   # Add your new repository:"
echo "   git remote add origin <your-new-repo-url>"
echo "   git push -u origin main"
echo ""
echo "Option 2: Use a branch in an existing repository"
echo "----------------------------------------"
echo "1. Create a new branch (from the $DEPLOY_DIR directory):"
echo "   git checkout -b minimal-render"
echo "2. Force push to the new branch:"
echo "   git push -u origin minimal-render --force"
echo ""
echo "3. Deploy to Render following the instructions in UPDATED_DEPLOY_INSTRUCTIONS.md"
echo ""
echo "The minimal deployment is ready in: $DEPLOY_DIR"
echo ""
echo "For detailed instructions, see UPDATED_DEPLOY_INSTRUCTIONS.md"
