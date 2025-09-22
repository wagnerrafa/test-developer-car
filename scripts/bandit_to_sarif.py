#!/usr/bin/env python3
"""Script para converter relatórios do Bandit de JSON para SARIF."""

import json
import os
import sys
from datetime import datetime, timezone


def convert_bandit_to_sarif(bandit_json_path: str, sarif_output_path: str) -> None:
    """
    Convert a Bandit report from JSON to SARIF format.

    Args:
        bandit_json_path: Caminho para o arquivo JSON do Bandit
        sarif_output_path: Caminho para o arquivo SARIF de saída

    """
    # Lê o arquivo JSON do Bandit
    with open(bandit_json_path, encoding="utf-8") as f:
        bandit_data = json.load(f)

    # Cria a estrutura SARIF
    sarif_data = {
        "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Bandit",
                        "version": "1.8.5",
                        "informationUri": "https://bandit.readthedocs.io/",
                        "rules": [],
                    }
                },
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "commandLine": f"bandit -r apps config -f json -o {bandit_json_path} --skip B101,B601,B106",
                        "startTimeUtc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                ],
                "results": [],
            }
        ],
    }

    # Converte os resultados do Bandit para SARIF
    if "results" in bandit_data:
        for result in bandit_data["results"]:
            sarif_result = {
                "ruleId": result.get("issue_text", "BANDIT_ISSUE"),
                "level": _convert_severity_to_level(result.get("issue_severity", "MEDIUM")),
                "message": {"text": result.get("issue_text", "Security issue found")},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": result.get("filename", "").replace("\\", "/")},
                            "region": {
                                "startLine": result.get("line_number", 1),
                                "startColumn": 1,
                                "endLine": result.get("line_number", 1),
                                "endColumn": 1,
                            },
                        }
                    }
                ],
                "properties": {
                    "confidence": result.get("issue_confidence", "MEDIUM"),
                    "severity": result.get("issue_severity", "MEDIUM"),
                    "test_id": result.get("test_id", ""),
                    "test_name": result.get("test_name", ""),
                },
            }
            sarif_data["runs"][0]["results"].append(sarif_result)

    # Se não há resultados, cria um SARIF vazio mas válido
    if not sarif_data["runs"][0]["results"]:
        sarif_data["runs"][0]["results"] = []

    # Escreve o arquivo SARIF
    with open(sarif_output_path, "w", encoding="utf-8") as f:
        json.dump(sarif_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Relatório SARIF gerado: {sarif_output_path}")
    print(f"📊 {len(sarif_data['runs'][0]['results'])} resultados convertidos")


def _convert_severity_to_level(severity: str) -> str:
    """
    Convert Bandit severity to SARIF level.

    Args:
        severity: Severidade do Bandit (LOW, MEDIUM, HIGH)

    Returns:
        Nível SARIF (note, warning, error)

    """
    severity_map = {"LOW": "note", "MEDIUM": "warning", "HIGH": "error"}
    return severity_map.get(severity.upper(), "warning")


def main():
    """Função principal do script."""
    if len(sys.argv) != 3:
        print("Uso: python bandit_to_sarif.py <bandit_json_file> <sarif_output_file>")
        print("Exemplo: python bandit_to_sarif.py bandit-report.json bandit-report.sarif")
        sys.exit(1)

    bandit_json_path = sys.argv[1]
    sarif_output_path = sys.argv[2]

    if not os.path.exists(bandit_json_path):
        print(f"❌ Arquivo não encontrado: {bandit_json_path}")
        sys.exit(1)

    try:
        convert_bandit_to_sarif(bandit_json_path, sarif_output_path)
    except Exception as e:
        print(f"❌ Erro ao converter: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
