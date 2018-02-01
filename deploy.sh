BRANCH="$(git rev-parse --abbrev-ref HEAD)"

if [ $BRANCH == "master" ]; then
    echo "Deployment starting..."
    # ssh-keyscan -H opencult.com >> ~/.ssh/known_hosts
    git push dokku@opencult.com:opencult master
else
    echo "Not on master, deployment canceled."
fi
