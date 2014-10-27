cat hg_repos | while read i
do j=$(echo $i| sed 's"/"_"')
   hg log -v --style ~audris/bin/multiline1 bitbucket.org_$j | gzip > bitbucket.org_$j.log.gz
done
