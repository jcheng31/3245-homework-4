index:
	python src/index.py -i patsnap-corpus -d run/dictionary.txt

search:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q1.xml -o run/output.txt

search2:
	python src/search.py -d run/dictionary.txt -p run/postings.txt \
		-q queries/q2.xml -o run/output.txt
