from python:3

RUN pip install flask flask_jwt_extended \
 && useradd -m -U -u 12345 avm

COPY --chown=avm:avm setup.py /home/avm/
COPY --chown=avm:avm README.md /home/avm/
COPY --chown=avm:avm src /home/avm/src

RUN pip install /home/avm/

USER avm
ENTRYPOINT ["avmb"]
