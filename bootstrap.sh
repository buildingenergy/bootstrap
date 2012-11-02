python -c "$(curl -fsSkL https://raw.github.com/buildingenergy/bootstrap/master/bootstrap.py)";
. ~/.flintrc;
flint sharpen;
rm /tmp/be.sh;
