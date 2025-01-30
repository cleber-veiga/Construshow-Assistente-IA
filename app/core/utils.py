import threading

# Eventos globais para indicar quando os recursos pesados estão carregados
tensorflow_load = threading.Event()
spacy_load = threading.Event()