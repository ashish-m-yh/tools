DBHOST=$1
DBUSER=$2
PASSWD=$3

for db in `mysql -h $DBHOST -u $DBUSER -p$DBPASS -e 'show databases' | grep ipay`
do
        count=`echo -n mysql -h $DBHOST -u $DBUSER -p$DBPASS -e \'SELECT SUM\(TABLE_ROWS\) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = \"$db\"\' | bash 2>/dev/null`
        echo $db $count
done
