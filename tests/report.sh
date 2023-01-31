SUCCESS=$(grep -c 'SUCCESS:' /tmp/logfile)
FAILED=$(grep -v -c 'SUCCESS:' /tmp/logfile)

if ( [ $SUCCESS != 1 ] || [ $FAILED != 7 ] )
then
  echo "Bad results for test"
  exit 1
else
  echo "Test is OK"
fi
