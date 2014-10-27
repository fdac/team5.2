cat git_repos | while read i
git --git-dir=$i log --numstat -M -C --diff-filter=ACMR --full-history \
 --pretty=tformat:"STARTOFTHECOMMIT%n%H;%T;%P;%an;%ae;%at;%cn;%ce;%ct;%s" \
 | perl ~audris/bin/extrgit.perl | gzip > $i.delta.gz
