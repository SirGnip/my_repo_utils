set -e

source venv/Scripts/activate
python -m my_repo_utils.my_repo_utils

cd data
cp repo_traffic.csv repo_traffic.$(date +%Y%m%d).csv

#echo
#echo -n Master file line count before appending:
#wc -l master_repo_traffic.csv

echo
echo Running data merge sript
source ../../csv_appender/venv/Scripts/activate
python -m csv_appender.csv_appender repo_traffic.csv master_repo_traffic.csv 1 2

echo
echo -n Master file line count after appending:
wc -l master_repo_traffic.csv


