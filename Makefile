index:
	python index.py -i patsnap-corpus -d dictionary.txt -p postings.txt

search:
	python search.py -d dictionary.txt -p postings.txt \
		-q queries/q1.xml -o output.txt

search2:
	python search.py -d dictionary.txt -p postings.txt \
		-q queries/q2.xml -o output.txt
