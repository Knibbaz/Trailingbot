FROM python:3.6

RUN mkdir /code  
WORKDIR /code  
ADD . /code/
RUN pip install --upgrade pip
RUN pip install requests datetime
RUN pip3 install --upgrade pip
 
CMD ["python3", "/code/test.py"]`