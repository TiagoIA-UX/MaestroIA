import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None):
    print(f"\n[EXECUTANDO] {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise Exception(f"Erro ao executar: {command}")
    return result.stdout

def run_tests():
    print("\n[TESTES] Executando testes automatizados...")
    try:
        output = run_command(f"{sys.executable} -m unittest discover -s maestroia/tests -p 'test_*.py'")
        if 'Ran 0 tests' in output:
            print("[ERRO] Nenhum teste foi encontrado. Verifique se há testes implementados em maestroia/tests.")
            return None
    except Exception as e:
        print("[FALHA NOS TESTES]", e)
        return False
    print("[TESTES] Todos os testes passaram.")
    return True

def refactor_code():
    print("\n[REFACTORIZAÇÃO] Aplicando autopep8 e isort...")
    try:
        run_command(f"{sys.executable} -m pip install autopep8 isort")
        run_command(f"{sys.executable} -m autopep8 --in-place --recursive maestroia/")
        run_command(f"{sys.executable} -m isort maestroia/")
    except Exception as e:
        print("[ERRO NA REFACTORIZAÇÃO]", e)
        return False
    print("[REFACTORIZAÇÃO] Código refatorado com sucesso.")
    return True

def main():
    print("""
==============================
 MaestroIA - Orquestração de Inovação
==============================
""")
    etapas = [
        "Implementar orquestração autônoma de agentes",
        "Integrar plataformas locais e globais (ex: RD Station, Google Analytics)",
        "Adicionar monitoramento de tendências (Google Trends, SEMrush)",
        "Personalizar recursos para profissionais femininas",
        "Aprimorar privacidade e conformidade (LGPD)",
        "Inovar em IA para insights personalizados",
        "Ajustar planos de preço e acessibilidade",
        "Otimizar SEO e parcerias locais",
    ]
    for i, etapa in enumerate(etapas, 1):
        print(f"\n[ETAPA {i}] {etapa}")
        input(f"Implemente a etapa acima e pressione ENTER para continuar para os testes...")
        while True:
            test_result = run_tests()
            if test_result is None:
                print("[ABORTADO] O ciclo foi interrompido porque não há testes automatizados.")
                return
            if test_result:
                break
            print("[AÇÃO] Corrija os erros e pressione ENTER para refazer os testes...")
            input()
        refactor_code()
        print(f"[ETAPA {i}] Concluída com sucesso!\n")
    print("\n==============================\nProjeto MaestroIA finalizado com sucesso!\n==============================")

if __name__ == "__main__":
    main()
