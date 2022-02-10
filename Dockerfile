FROM python:3.6

RUN mkdir /code  
WORKDIR /code  
ADD . /code/
RUN pip install --upgrade pip 
RUN pip3 install --upgrade pip
RUN pip install python-dotenv python_bitvavo_api requests datetime icecream
RUN pip3 install python-dotenv python_bitvavo_api requests datetime icecream
 
CMD ["python3", "/code/test.py"]`