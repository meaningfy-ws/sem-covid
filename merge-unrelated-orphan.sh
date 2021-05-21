
THIS_BRANCH=$1

# checkout to this branch and get the latest version
git checkout $THIS_BRANCH
git pull origin $THIS_BRANCH

# to get rid of the history on a given branch
git checkout --orphan latest_branch
git add -A
git commit -am "commit unrelated history"
git branch -D $THIS_BRANCH
git branch -m $THIS_BRANCH
#git push -f origin $THIS_BRANCH

# merge main
git checkout main
git pull
git checkout $THIS_BRANCH
git merge main --allow-unrelated-histories

# THIS is the place where you usually solve manually the conflicts
# then solve the conflicts

git commit -ma "unrelated branches merged; hopefully without conflicts"
git push --force origin $THIS_BRANCH
