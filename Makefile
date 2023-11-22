setup: 
	echo "setting up tensor IOT"
	python3 -m venv tensorIOT
	./tensorIOT/bin/activate 

run: 
	echo "running task"
	python3 task.py