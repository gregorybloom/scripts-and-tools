
exit;

# Clean up filenames recursively; it _may_ need to be re-run for renamed parent folders
IFS=$'\n'; for file in $(find . -print -depth); do if echo "$file" | grep -qP ".*['\&\!\"\#\(\)\~]"; then file_clean=${file//[\"\#\!()&\'\~]/_}; mv -v "$file" "$file_clean"; fi; done

# .zip's any subfolders, but only those subfolders
IFS=$'\n'; for folder in $(find ./ -maxdepth 1 -type d -print); do if echo "$folder" | grep -qP "^\.\/\w+"; then pushd "$folder"; for file in $(ls -1); do zip -r "$file.zip" "$file"; done; popd; fi; done

# delete empty folders at least 2 depth in.  Remove '-depth' to only prune current leaf nodes, not all directory trees
find "folderpath/to/target/" -type d -mindepth 2 -depth -exec rmdir -v {} \; 2>/dev/null


#------------------------------------------
# Rewrite Git History (remove bad commits from git and github)

# SET ASIDE/BACK-UP YOUR CHANGES!!
# This will remove any changes you've made from your files

# remove last commit (or repeat for more)
git reset HEAD^
git push origin +HEAD
git add -A; git commit -m
git filter-branch --tree-filter 'rm -rf secure_data/_datadonotshare/' --prune-empty HEAD
git push
