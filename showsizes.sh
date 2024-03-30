find . -exec stat -c "%s %n" {} \; | sort -n
