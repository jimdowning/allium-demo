#!/usr/bin/env sh
# Create the four stage tags on their commits. Run once after cloning or
# forking if the tags are missing (git tag -l 'stage-*' prints nothing).
# Add --push to also push them to origin.
set -e
git tag -f stage-0-brief     c241c76d6c27254bc707d3c2f3defac01505e490
git tag -f stage-1-elicit    dad8b032ab0d4ce1645572f583d732f66553669e
git tag -f stage-2-propagate 6f887e67819364a56436d0f9f907e2a8fb7c1298
git tag -f stage-3-fixed     0b55e4f980059db3f0c9a2bf6966375de61897bc
if [ "$1" = "--push" ]; then
    git push -f origin stage-0-brief stage-1-elicit stage-2-propagate stage-3-fixed
fi
