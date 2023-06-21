#/bin/sh
pstr='\u001b[0m\u001b[1mPlease specify if this is an agent/satellite setup (\'n\' installs a master setup)\u001b[0m [Y/n]: ' # plain, un-escaped string
estr=$(perl -e 'print quotemeta shift(@ARGV)' "${pstr}")
echo ${estr}