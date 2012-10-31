#!/bin/bash
python -c "$(curl -fsSkL https://raw.github.com/buildingenergy/bootstrap/master/bootstrap.py)"
. ~/.bash_profile
flint update-autocomplete
