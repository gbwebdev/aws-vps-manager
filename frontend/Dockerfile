from python:3

RUN pip install flask flask_jwt_extended passlib flask_sqlalchemy \
 && useradd -m -U -u 12345 avm \
 && mkdir /var/avm \
 && chown avm /var/avm

COPY --chown=avm:avm src /home/avm/src

USER avm
WORKDIR "/home/avm"
ENTRYPOINT ["python"]
CMD ["/home/avm/src/app.py"]
