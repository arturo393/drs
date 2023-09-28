#!/bin/sh

END=${1:-"local"}

echo $END

if [ $END = "local" ]; then
    sed -i '/IgnoreSlave/'d /var/www/*.html

    sed -i '/ssfb.html/i\<!--IgnoreSlave' /var/www/index.html
    sed -i '/ssfb.html/a\IgnoreSlave-->' /var/www/index.html
    sed -i '/1m_drag_16s_tr_begin/i\<!--IgnoreSlave' /var/www/msfb.html
    sed -i '/1m_drag_16s_tr_end/a\IgnoreSlave-->' /var/www/msfb.html
    sed -i '/pa.html/i\<!--IgnoreSlave' /var/www/index.html
    sed -i '/pa.html/a\IgnoreSlave-->' /var/www/index.html
    sed -i '/lna.html/i\<!--IgnoreSlave' /var/www/index.html
    sed -i '/lna.html/a\IgnoreSlave-->' /var/www/index.html

    sed -i '/IgnoreMaster/'d /var/www/*.html

    echo "Shifted web code to master!"

elif [ $END = "remote" ]; then
    sed -i '/IgnoreMaster/'d /var/www/*.html

    sed -i '/msfb.html/i\<!--IgnoreMaster' /var/www/index.html
    sed -i '/msfb.html/a\IgnoreMaster-->' /var/www/index.html

    sed -i '/IgnoreSlave/'d /var/www/*.html

    echo "Shifted web code to slave!"
else
    echo "Usage: sh web_L-R_shift.sh <local/remote>"
fi
