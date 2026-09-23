"""
El "main" que ejecutas en consola
"""

from langgraph.types import Command
from agent.graph import construir_grafo

def main():
    grafo = construir_grafo()
    config = {"configurable": {"thread_id": "consola-1"}}

    resultado = grafo.invoke({}, config=config)

    while "__interrupt__" in resultado:
        pregunta = resultado["__interrupt__"][0].value
        print(f"Agente: {pregunta}")
        respuesta = input("Usuario: ")
        resultado = grafo.invoke(Command(resume=respuesta), config=config)

if __name__ == "__main__":
     main()